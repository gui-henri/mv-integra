from fastapi import APIRouter, Depends, HTTPException
import oracledb
from app.dependencies import get_db_connection
from app.core.logger import logger
from app.services.profitability_analisys import calculate_profitability

router = APIRouter(
    prefix="/mv",
    tags=["MV Integration"]
)

from app.schemas.invoice import Invoice, InvoiceItem

@router.get("/get-rentability")
def get_rentability(
    cd_orcamento: int,
    conn: oracledb.Connection = Depends(get_db_connection)):
    try:
        cursor = conn.cursor()
        # Gets the header of the invoice
        queryHeader = """
                    SELECT
                        O.CD_ORCAMENTO,
                        P.CD_PACIENTE,
                        P.NM_PACIENTE,
                        O.DT_ORCAMENTO,
                        C.NM_CONVENIO,
                        A.DT_ATENDIMENTO,
                        A.DT_ALTA -- pode não existir
                    FROM dbamv.ORCAMENTO_HOCA O
                    JOIN dbamv.PACIENTE P ON O.CD_PACIENTE = P.CD_PACIENTE
                    JOIN dbamv.CONVENIO C ON O.CD_CONVENIO = C.CD_CONVENIO
                    JOIN dbamv.ATENDIME A ON O.CD_ATENDIMENTO = A.CD_ATENDIMENTO
                    WHERE O.CD_ORCAMENTO = :cd_orcamento;
                """
        cursor.execute(queryHeader, cd_orcamento=cd_orcamento)
        resultHeader = cursor.fetchall()
        
        # Gets the items of the invoice
        queryItems = """
                        SELECT
                            I.CD_PRO_FAT,
                            I.DS_PRO_FAT AS DESCRICAO_ITEM,
                            I.QTDE,
                            I.VL_PRO_FAT,
                            I.VL_CUSTO,
                            G.CD_GRU_PRO,
                            G.DS_GRU_PRO AS DESCRICAO_GRUPO
                        FROM
                            ITORCAMENTO_HOCA I
                        INNER JOIN
                            dbamv.PRO_FAT P ON I.CD_PRO_FAT = P.CD_PRO_FAT
                        INNER JOIN
                            dbamv.GRU_PRO G ON P.CD_GRU_PRO = G.CD_GRU_PRO
                        WHERE
                            I.CD_ORCAMENTO = :cd_orcamento;
                    """
        cursor.execute(queryItems, cd_orcamento=cd_orcamento)
        resultItems = cursor.fetchall()

        if not resultHeader:
             raise HTTPException(status_code=404, detail="Orcamento not found")

        invoice = Invoice(
            cd_orcamento=resultHeader[0][0],
            cd_paciente=resultHeader[0][1],
            nm_paciente=str(resultHeader[0][2]),
            dt_orcamento=str(resultHeader[0][3]),
            cd_convenio=resultHeader[0][4],
            nm_convenio=str(resultHeader[0][5]),
            cd_atendimento=resultHeader[0][6],
            dt_atendimento=str(resultHeader[0][7]) if resultHeader[0][7] else "",
            dt_alta=str(resultHeader[0][8]) if resultHeader[0][8] else None,
            items=[InvoiceItem(
                descricao=str(item[1] or ""),
                quantidade=float(item[2] or 0.0),
                unidade="UN",
                valor_total=float(item[3] or 0.0), # Assuming VL_PRO_FAT is total
                valor_unitario=(float(item[3] or 0.0) / float(item[2])) if (item[2] and float(item[2]) != 0) else 0.0,
                grupo_procedimento=str(item[6] or ""),
                custo_total=float(item[4] or 0.0),
                custo_unitario=(float(item[4] or 0.0) / float(item[2])) if (item[2] and float(item[2]) != 0) else 0.0,
            ) for item in resultItems]
        )

        res = calculate_profitability(invoice)

        cursor.close()
        return res
    except Exception as e:
        logger.error(f"Query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# 5.65% taxes
FATOR_LIQUIDO = 1 - (0.02 + 0.0065 + 0.03)

class CategoryResult(BaseModel):
    grupo_procedimento: str
    receita_bruta: float
    receita_liquida: float
    custos_mv: float
    custos_fixos: float
    margem_bruta: float
    impostos: float
    margem_liquida: float

class InvoiceProfitabilityResponse(BaseModel):
    category_results: list[CategoryResult]
    total_receita_bruta: float
    total_receita_liquida: float
    total_custos_mv: float
    total_custos_fixos: float
    total_margem_bruta: float
    total_impostos: float
    total_margem_liquida: float
    rentabilidade: float

class InvoiceItem(BaseModel):
    descricao: str
    quantidade: float
    unidade: str
    valor_unitario: float
    valor_total: float
    grupo_procedimento: str
    custo_unitario: float
    custo_total: float
    pacote: str = "SIM"

class Invoice(BaseModel):
    cd_orcamento: int
    cd_paciente: int
    nm_paciente: str
    dt_orcamento: str
    cd_convenio: int
    nm_convenio: str
    cd_atendimento: int
    dt_atendimento: str
    dt_alta: Optional[str] = None
    pacote: str = "NÃO"
    items: list[InvoiceItem]

    def __init__(self, **data):
        super().__init__(**data)
        # Check if items are loaded and logic needs to run
        if self.items:
            for item in self.items:
                if item.grupo_procedimento == "DIARIAS":
                    item.pacote = "NÃO"
                    self.pacote = "SIM"
                else:
                    item.pacote = "SIM" # Default is SIM but we enforce logic

    @property
    def complexity(self) -> str:
        for item in self.items:
            if item.grupo_procedimento == "DIARIAS":
                desc = item.descricao.upper()
                if "ALTA" in desc: return "ALTA COMPLEXIDADE"
                if "MEDIA" in desc or "MÉDIA" in desc: return "MEDIA COMPLEXIDADE"
                if "BAIXA" in desc: return "BAIXA COMPLEXIDADE"
        return "BAIXA COMPLEXIDADE"

    @property
    def duration_days(self) -> int:
        try:
            dt_atd = datetime.fromisoformat(str(self.dt_atendimento).replace(' ', 'T')) if self.dt_atendimento else None
            dt_alt = datetime.fromisoformat(str(self.dt_alta).replace(' ', 'T')) if self.dt_alta else datetime.now()
        except:
             return 1
             
        if dt_atd and dt_alt:
            delta = (dt_alt - dt_atd).days
            return delta if delta > 0 else 1
        return 1

    def custos_mv(self, categoria: str):
        total = 0.0
        for item in self.items:
            if item.grupo_procedimento == categoria:
                total += item.custo_total
        return total

    def receita_categoria(self, categoria: str):
        total_bruto = 0.0
        total_liquido = 0.0
        for item in self.items:
            if item.grupo_procedimento == categoria and item.pacote == "NÃO":
                total_bruto += item.valor_total
                total_liquido += item.valor_total * FATOR_LIQUIDO
        return total_bruto, total_liquido

    def margem_bruta_categoria(self, categoria: str, rv: float, cmv: float, cfix: float):
        return rv - cmv - cfix
        
    def impostos_categoria(self, rv: float):
        return 0.0
        
    def margem_liquida_categoria(self, mb: float, imp: float):
        return mb - imp

from app.schemas.invoice import Invoice, InvoiceProfitabilityResponse, CategoryResult

# Constants from notebook
TAXA_IMPOSTOS = 0.02 + 0.0065 + 0.03 # 5.65%
FATOR_LIQUIDO = 1 - TAXA_IMPOSTOS
MULTIPLICADOR_CUSTO_TOTAL = 1.1
ALIQUOTA_IMPOSTO_RENDA = 0.34

TIPOS_SERVICO = {
    "Internação Domiciliar 6hrs": 50,
    "Internação Domiciliar 12hrs": 100,
    "Internação Domiciliar 24hrs": 200,
    "Assistência Domiciliar": 35,
    "Terapias": 9,
    "Curabem": 28.8,
    "Oxigenoterapia": 11.6,
    "Fiqbem": 3.10
}

MAP_CUSTOS = {
    "BAIXA COMPLEXIDADE": "Internação Domiciliar 6hrs",
    "MEDIA COMPLEXIDADE": "Internação Domiciliar 12hrs",
    "ALTA COMPLEXIDADE": "Internação Domiciliar 24hrs"
}

GRUPOS_PROCEDIMENTOS = [
    "DIARIAS",
    "TAXAS",
    "SERV ENFERMAGEM",
    "SERVICOS DE FISIOTERAPIA",
    "SERVICOS DE FONOAUDIOLOGIA",
    "SERVICOS DE NUTRICAO",
    "SERVICOS DE TERAPIA OCUPACIONAL",
    "VISITAS E CONSULTAS MEDICAS - HC",
    "MEDICAMENTOS",
    "MEDICAMENTOS RESTRITO HOSP.",
    "ALIMENTACOES E DIETAS",
    "MATERIAIS",
    "CURATIVOS ESPECIAIS"
]

def custo_fixo_total(tipo_servico: str, periodo: int) -> float:
    # Handle cases where tipo_servico might not be in the dictionary if logic changes, but here we assume it is.
    # Defaulting to 0 if not found could be safer.
    servico_custo = TIPOS_SERVICO.get(tipo_servico, 0)
    custo_total = servico_custo * periodo
    return custo_total

def calculate_profitability(invoice: Invoice) -> InvoiceProfitabilityResponse:
    quantidade_dias = invoice.duration_days
    complexidade = invoice.complexity
    
    # Calculate global parameters
    # Determine service type from complexity. Note: Notebook has explicit mapping. 
    # If complexity not in map (e.g. unknown), fallback?
    tipo_servico = MAP_CUSTOS.get(complexidade, "Internação Domiciliar 6hrs") 
    
    # Base fixed cost
    base_cfixo = custo_fixo_total(tipo_servico, quantidade_dias)
    total_custo_fixo_geral = round(base_cfixo * MULTIPLICADOR_CUSTO_TOTAL, 2)

    categories = []
    
    total_receita_bruta = 0.0
    total_receita_liquida = 0.0
    total_custos_mv = 0.0
    total_custos_fixos_sum = 0.0
    
    # First pass: Calculate revenues and costs per category
    # We need to collect margins to calculate taxes later if we want to follow notebook exactly
    # Notebook: 
    #   Calculate per-row: Receita Bruta, Receita Liquida, Custos MV, Custos Fixos (only for TAXAS)
    #   Calculate per-row: Margem Bruta = RL - (CMV + CF)
    #   Then Sum Margem Bruta
    #   Then Calculate Total Impostos logic
    #   Then Distribute Impostos (Taxa Rateio)
    
    temp_results = []

    for categoria in GRUPOS_PROCEDIMENTOS:
        # Use Invoice methods for simple sums
        rec_bruta, rec_liquida = invoice.receita_categoria(categoria)
        c_mv = invoice.custos_mv(categoria)
        
        # Apply Fixed Cost only to 'TAXAS'
        c_fixo = total_custo_fixo_geral if categoria == "TAXAS" else 0.0
        
        margem_bruta = rec_liquida - c_mv - c_fixo
        
        result_entry = {
            "grupo_procedimento": categoria,
            "receita_bruta": rec_bruta,
            "receita_liquida": rec_liquida,
            "custos_mv": c_mv,
            "custos_fixos": c_fixo,
            "margem_bruta": margem_bruta
        }
        temp_results.append(result_entry)
        
        total_receita_bruta += rec_bruta
        total_receita_liquida += rec_liquida
        total_custos_mv += c_mv
        total_custos_fixos_sum += c_fixo

    # Calculate Total Margin
    total_margem_bruta = total_receita_liquida - (total_custos_mv + total_custos_fixos_sum)
    
    # Calculate Total Impostos (Income Tax on Profit)
    # Notebook: impostos = margem_bruta * 0.34 if margem_bruta > 0 else 0
    total_impostos = total_margem_bruta * ALIQUOTA_IMPOSTO_RENDA if total_margem_bruta > 0 else 0.0
    
    # Calculate Rateio
    # Notebook: sum of POSITIVE margins
    margem_bruta_positiva_total = sum(item["margem_bruta"] for item in temp_results if item["margem_bruta"] > 0)
    
    if margem_bruta_positiva_total > 0:
        taxa_rateio = total_impostos / margem_bruta_positiva_total
    else:
        taxa_rateio = 0.0
        
    # Second pass: Apply taxes and create CategoryResult objects
    category_results_objects = []
    
    calculated_total_impostos = 0.0 # To verify sums
    
    for item in temp_results:
        mb = item["margem_bruta"]
        imposto_item = (mb * taxa_rateio) if mb > 0 else 0.0
        calculated_total_impostos += imposto_item
        
        ml = mb - imposto_item
        
        cat_result = CategoryResult(
            grupo_procedimento=item["grupo_procedimento"],
            receita_bruta=round(item["receita_bruta"], 2),
            receita_liquida=round(item["receita_liquida"], 2),
            custos_mv=round(item["custos_mv"], 2),
            custos_fixos=round(item["custos_fixos"], 2),
            margem_bruta=round(mb, 2),
            impostos=round(imposto_item, 2),
            margem_liquida=round(ml, 2)
        )
        category_results_objects.append(cat_result)
        
    total_margem_liquida = total_margem_bruta - total_impostos
    
    # Rentabilidade
    rentabilidade = (total_margem_liquida / total_receita_liquida * 100) if total_receita_liquida else 0.0

    return InvoiceProfitabilityResponse(
        category_results=category_results_objects,
        total_receita_bruta=round(total_receita_bruta,2),
        total_receita_liquida=round(total_receita_liquida,2),
        total_custos_mv=round(total_custos_mv,2),
        total_custos_fixos=round(total_custos_fixos_sum,2),
        total_margem_bruta=round(total_margem_bruta,2),
        total_impostos=round(total_impostos,2),
        total_margem_liquida=round(total_margem_liquida,2),
        rentabilidade=round(rentabilidade,2)
    )
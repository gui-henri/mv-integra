TAXA_TOTAL               = 0.02 + 0.0065 + 0.03 # 5,65%
FATOR_LIQUIDO            = 1 - TAXA_TOTAL
MULTIPLICADOR_CUSTO_TOTAL = 1.1
TAXA_IMPOSTOS            = 0.34


GrupoProcedimentos = [
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
	"CURATIVOS ESPECIAIS",
]

ServiceTypes = {
	"Internação Domiciliar 6hrs":  50,
	"Internação Domiciliar 12hrs": 100,
	"Internação Domiciliar 24hrs": 200,
	"Assistência Domiciliar":      35,
	"Terapias":                    9,
	"Curabem":                     28.8,
	"Oxigenoterapia":              11.6,
	"Fiqbem":                      3.10,
}

MapCustos = {
	"BAIXA COMPLEXIDADE": "Internação Domiciliar 6hrs",
	"MEDIA COMPLEXIDADE": "Internação Domiciliar 12hrs",
	"ALTA COMPLEXIDADE":  "Internação Domiciliar 24hrs",
}


def custo_fixo_total(service_type: str, period: int) -> float:
	servico_custo = ServiceTypes[service_type]
	custo_total = servico_custo * float(period)
	return custo_total

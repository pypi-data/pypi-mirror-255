from pyspedfiscal.campos import CampoEnumerate


class CodSit(CampoEnumerate):
    """Tabela 4.1.2 - Código da Situação do Documento"""

    regular = "00"
    extemporaneo = "01"
    cancelado = "02"
    cancelado_extemporaneo = "03"
    denegado = "04"
    inutilizado = "05"
    complementar = "06"
    complementar_extemporaneo = "07"
    regime_especial = "08"


class CodMod(CampoEnumerate):
    """Tabela 4.1.1 - Tabela Documentos Fiscais do ICMS"""

    nota_fiscal = "01"
    nota_fiscal_avulsa = "1B"
    nota_fiscal_de_venda_consumidor = "02"
    cupom_fiscal = "2D"
    cupom_fiscal_passagem = "2E"
    nota_fiscal_produtor = "04"
    energia_eletrica = "06"
    nota_fiscal_transporte = "07"
    conhecimento_de_transporte = "08"
    conhecimento_de_transporte_avulso = "8B"
    conhecimento_de_transporte_aquaviario = "09"
    conhecimento_aereo = "10"
    conhecimento_de_transporte_ferroviario = "11"
    bilhete_de_passagem_rodoviario = "13"
    bilhete_de_passagem_aquaviario = "14"
    bilhete_de_passagem_nota_bagagem = "15"
    bilhete_de_passagem_ferroviario = "16"
    resumo_de_movimento_diario = "18"
    nota_fiscal_servico_de_comunicacao = "21"
    nota_fiscal_servico_de_telecomunicacao = "22"
    conhecimento_de_transporte_multimodal = "26"
    nota_fiscal_transporte_ferroviario = "27"
    nota_fiscal_gas_canalizado = "28"
    nota_fiscal_agua_canalizada = "29"
    nota_fiscal_eletronica = "55"
    conhecimento_de_transporte_eletronico = "57"
    cupom_fiscal_eletronico_sat = "59"
    cupom_fiscal_eletronico_secf = "60"
    bilhete_de_passagem_eletronico = "63"
    nota_fiscal_eletronica_consumidor_final = "65"
    conhecimento_de_transporte_eletronico_os = "67"


class CodModIss(CampoEnumerate):
    """Tabela 4.1.1 - Tabela Documentos Fiscais do ISS"""

    nota_fiscal = "1/1 A"
    nota_fiscal_servico = "3"
    nota_fiscal_servico_simp = "3A"
    nota_fiscal_servico_avulso = "3B"
    nota_fiscal_produtor = "4"
    conhecimento_transporte = "8"
    nota_fiscal_eletronica = "55"
    nota_fiscal_eletronica_consumidor_final = "65"
    nota_fiscal_energia_eletrica_eletronica = "66"


class CodVer(CampoEnumerate):
    """Tabela 3.1.1 - Tabela Versão do Leiaute - Sped Fiscal"""

    layout_1_01 = "002"
    layout_1_02 = "003"
    layout_1_03 = "004"
    layout_1_04 = "005"
    layout_1_05 = "006"
    layout_1_06 = "007"
    layout_1_07 = "008"
    layout_1_08 = "009"
    layout_1_09 = "010"
    layout_1_10 = "011"
    layout_1_11 = "012"
    layout_1_12 = "013"
    layout_1_13 = "014"
    layout_1_14 = "015"
    layout_1_15 = "016"
    layout_1_16 = "017"
    layout_1_17 = "018"


class GenItemMercServ(CampoEnumerate):
    """Tabela 4.2.1 - Tabela Gênero do Item de Mercadoria/Serviço"""

    pass


class ClassifContribIpi(CampoEnumerate):
    """Tabela 4.5.5 - Classificação de Contribuintes do IPI"""

    industrial_transformacao = "00"
    industrial_beneficiamento = "01"
    industrial_montagem = "02"
    industrial_acondicionamento_reacondicionamento = "03"
    industrial_renovacao_recondicionamento = "04"
    equiparado_opcao = "05"
    equiparado_importacao_direta = "06"
    equiparado_por_lei_especifica = "07"
    equiparado_nao_enquadrado = "08"
    outros = "99"

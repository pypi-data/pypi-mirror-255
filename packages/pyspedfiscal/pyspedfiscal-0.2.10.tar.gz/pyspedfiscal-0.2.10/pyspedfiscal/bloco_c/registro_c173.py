from typing import Literal
from pyspedfiscal.campos import CampoDecimal, CampoAlphanumerico, CampoData, CampoEnumerate
from pyspedfiscal.models import Registro


class IndMed(CampoEnumerate):
    """ 
    Indicador de tipo de referência da base de
    cálculo do ICMS (ST) do produto farmacêutico
    """
    tabelado_sugerido = '0'
    margem_valor_agregado = '1'
    lista_negativa = '2'
    lista_positiva = '3'
    lista_neutra = '4'


class TpProduto(CampoEnumerate):
    """ Tipo de produto """
    similar = '0'
    generico = '1'
    etico_marca = '2'


class RegistroC173(Registro):
    """ OPERAÇÕES COM MEDICAMENTOS (CÓDIGO 01 e 55) """
    reg: Literal['C173']
    lote_med: CampoAlphanumerico
    qtd_item: CampoDecimal
    dt_fab: CampoData
    dt_val: CampoData
    ind_med: IndMed
    tp_prod: TpProduto
    vl_tab_max: CampoDecimal

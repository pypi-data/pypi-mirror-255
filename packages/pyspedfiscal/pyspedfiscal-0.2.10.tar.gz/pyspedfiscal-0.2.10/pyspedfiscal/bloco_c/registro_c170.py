from typing import Literal
from pyspedfiscal.campos import CampoDecimal, CampoInteiro, CampoAlphanumerico, CampoEnumerate
from pyspedfiscal.models import Registro


class IndMov(CampoEnumerate):
    """ Movimentação física do ITEM/PRODUTO: """
    sim = '0'
    nao = '1'


class IndAPur(CampoEnumerate):
    """ Indicador de período de apuração do IPI """
    mensal = '0'
    decendial = '1'


class RegistroC170(Registro):
    """ ITENS DO DOCUMENTO (CÓDIGO 01, 1B, 04 e 55) """

    reg: Literal['C170']
    num_item: CampoInteiro
    cod_item: CampoAlphanumerico
    descr_compl: CampoAlphanumerico
    qtd: CampoDecimal
    unid: CampoAlphanumerico
    vl_item: CampoDecimal
    vl_desc: CampoDecimal
    ind_mov: IndMov
    cst_icms: CampoInteiro
    cfop: CampoInteiro
    cod_nat: CampoAlphanumerico
    vl_bc_icms: CampoDecimal
    aliq_icms: CampoDecimal
    vl_icms: CampoDecimal
    vl_bc_icms_st: CampoDecimal
    aliq_st: CampoDecimal
    vl_icms_st: CampoDecimal
    ind_apur: IndAPur
    cst_ipi: CampoAlphanumerico
    cod_enq: CampoAlphanumerico
    vl_bc_ipi: CampoDecimal
    aliq_ipi: CampoDecimal
    vl_ipi: CampoDecimal
    cst_pis: CampoInteiro
    vl_bc_pis: CampoDecimal
    aliq_pis_percent: CampoDecimal
    quant_bc_pis: CampoDecimal
    aliq_pis: CampoDecimal
    vl_pis: CampoDecimal
    cst_cofins: CampoInteiro
    vl_bc_cofins: CampoDecimal
    aliq_cofins_percent: CampoDecimal
    quant_bc_cofins: CampoDecimal
    aliq_cofins: CampoDecimal
    vl_cofins: CampoDecimal
    cod_cta: CampoAlphanumerico
    vl_abat_nt: CampoDecimal

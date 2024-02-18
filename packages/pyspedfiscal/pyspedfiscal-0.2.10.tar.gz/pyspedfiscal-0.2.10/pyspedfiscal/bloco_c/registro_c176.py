from typing import Literal
from pyspedfiscal.campos import (
    CampoDecimal, CampoInteiro, CampoAlphanumerico, CampoSerie,
    CampoData, CampoEnumerate
)
from pyspedfiscal.models import Registro


class CodRespRet(CampoEnumerate):
    """ 
    Código que indica o responsável pela
    retenção do ICMS ST 
    """
    direto_regime_comum = '1'
    indireto = '2'
    proprio_declarante = '3'
    direto_simples_nacional = '4'


class CodMotRes(CampoEnumerate):
    """ Código do motivo do ressarcimento """
    saida_outra_uf = '1'
    saida_insecao_nao_incidencia = '2'
    perda_deterioracao = '3'
    furto_roubo = '4'
    exportacao = '5'


class CodDa(CampoEnumerate):
    """ Código do modelo do documento de arrecadação """
    dae = '0'
    gnre = '1'


class RegistroC176(Registro):
    """ 
    RESSARCIMENTO DE ICMS E FUNDO DE COMBATE À POBREZA (FCP)
    EM OPERAÇÕES COM SUBSTITUIÇÃO TRIBUTÁRIA (CÓDIGO 01, 55) 
    """
    reg: Literal['176']
    cod_mod_ult_e: CampoAlphanumerico
    num_doc_ult_e: CampoInteiro
    ser_ult_e: CampoSerie
    dt_ult_e: CampoData
    cod_part_ult_e: CampoAlphanumerico
    quant_ult_e: CampoDecimal
    vl_unit_ult_e: CampoDecimal
    vl_unit_bc_st: CampoDecimal
    chave_nfe_ult_e: CampoInteiro
    num_item_ult_e: CampoInteiro
    vl_unit_bc_icms_ult_e: CampoDecimal
    aliq_icms_ult_e: CampoDecimal
    vl_unit_limite_bc_icms_ult_e: CampoDecimal
    vl_unit_icms_ult_e: CampoDecimal
    aliq_st_ult_e: CampoDecimal
    vl_unit_res: CampoDecimal
    cod_resp_ret: CodRespRet
    cod_mot_res: CodMotRes
    chave_nfe_ret: CampoAlphanumerico
    cod_part_nfe_ret: CampoAlphanumerico
    ser_nfe_ret: CampoSerie
    num_nfe_ret: CampoInteiro
    item_nfe_ret: CampoInteiro
    cod_da: CodDa
    num_da: CampoAlphanumerico
    vl_unit_res_fcp_st: CampoDecimal

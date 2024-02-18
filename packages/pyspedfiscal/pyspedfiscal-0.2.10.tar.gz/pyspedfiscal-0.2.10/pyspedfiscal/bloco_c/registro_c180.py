from pyspedfiscal.campos import CampoDecimal, CampoAlphanumerico, CampoEnumerate
from pyspedfiscal.models import Registro
from typing import Literal


class CodRespRet(CampoEnumerate):
    """
    Código que indica o responsável pela
    retenção do ICMS ST
    """
    remetente_direto = '1'
    remetente_indireto = '2'
    proprio_declarante = '3'


class CodDa(CampoEnumerate):
    """ 
    Código do modelo do documento de
    arrecadação
    """
    dae = '0'
    gnre = '1'


class RegistroC180(Registro):
    """
    INFORMAÇÕES COMPLEMENTARES DAS OPERAÇÕES DE ENTRADA
    DE MERCADORIAS SUJEITAS À SUBSTITUIÇÃO TRIBUTÁRIA 
    (CÓDIGO 01, 1B, 04 e 55).
    """
    reg: Literal['C180']
    cod_resp_ret: CodRespRet
    quant_conv: CampoDecimal
    unid: CampoAlphanumerico
    vl_unit_conv: CampoDecimal
    vl_unit_icms_op_conv: CampoDecimal
    vl_unit_bc_icms_st_conv: CampoDecimal
    vl_unit_icms_st_conv: CampoDecimal
    vl_unit_fcp_st_conv: CampoDecimal
    cod_da: CodDa
    num_da: CampoAlphanumerico

from pyspedfiscal.campos import CampoDecimal, CampoInteiro, CampoAlphanumerico
from pyspedfiscal.models import Registro
from typing import Literal


class RegistroC185(Registro):
    """
    INFORMAÇÕES COMPLEMENTARES DAS OPERAÇÕES DE SAÍDA DE
    MERCADORIAS SUJEITAS À SUBSTITUIÇÃO TRIBUTÁRIA (CÓDIGO 01, 1B, 04, 55 e 65).
    """
    reg: Literal['C185']
    num_item: CampoInteiro
    cod_item: CampoAlphanumerico
    cst_icms: CampoInteiro
    cfop: CampoInteiro
    cod_mot_rest_compl: CampoAlphanumerico
    quant_conv: CampoDecimal
    unid: CampoAlphanumerico
    vl_unit_conv: CampoDecimal
    vl_unit_icms_na_operacao_conv: CampoDecimal
    vl_unit_icms_op_conv: CampoDecimal
    vl_unit_icms_op_estoque_conv: CampoDecimal
    vl_unit_icms_st_estoque_conv: CampoDecimal
    vl_unit_fcp_icms_st_estoque_conv: CampoDecimal
    vl_unit_icms_st_conv_rest: CampoDecimal
    vl_unit_fcp_st_conv_rest: CampoDecimal
    vl_unit_icms_st_conv_compl: CampoDecimal
    vl_unit_fcp_st_conv_compl: CampoDecimal

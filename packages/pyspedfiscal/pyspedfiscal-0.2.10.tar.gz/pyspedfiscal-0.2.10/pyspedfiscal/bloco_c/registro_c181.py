from pyspedfiscal.campos import CampoData, CampoDecimal, CampoInteiro, CampoAlphanumerico, CampoSerie
from pyspedfiscal.models import Registro
from typing import Literal


class RegistroC181(Registro):
    """
    INFORMAÇÕES COMPLEMENTARES DAS OPERAÇÕES DE
    DEVOLUÇÃO DE SAÍDAS DE MERCADORIAS SUJEITAS À SUBSTITUIÇÃO TRIBUTÁRIA
    (CÓDIGO 01, 1B, 04 e 55).
    """
    reg: Literal['C181']
    cod_mot_rest_compl: CampoAlphanumerico
    quant_conv: CampoDecimal
    unid: CampoAlphanumerico
    cod_mod_saida: CampoAlphanumerico
    serie_saida: CampoSerie
    ecf_fab_saida: CampoAlphanumerico
    num_doc_saida: CampoInteiro
    chv_dfe_saida: CampoInteiro
    dt_doc_saida: CampoData
    num_item_saida: CampoInteiro
    vl_unit_conv_saida: CampoDecimal
    vl_unit_icms_op_estoque_conv_saida: CampoDecimal
    vl_unit_icms_st_estoque_conv_saida: CampoDecimal
    vl_unit_fcp_icms_st_estoque_conv_saida: CampoDecimal
    vl_unit_icms_na_operacao_conv_saida: CampoDecimal
    vl_unit_icms_op_conv_saida: CampoDecimal
    vl_unit_icms_st_conv_rest: CampoDecimal
    vl_unit_fcp_st_conv_rest: CampoDecimal
    vl_unit_icms_st_conv_compl: CampoDecimal
    vl_unit_fcp_st_conv_compl: CampoDecimal

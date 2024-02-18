from pyspedfiscal.campos import CampoData, CampoDecimal, CampoInteiro, CampoAlphanumerico, CampoSerie
from pyspedfiscal.models import Registro
from typing import Literal


class RegistroC186(Registro):
    """
    INFORMAÇÕES COMPLEMENTARES DAS OPERAÇÕES DE
    DEVOLUÇÃO DE ENTRADAS DE MERCADORIAS SUJEITAS À SUBSTITUIÇÃO
    TRIBUTÁRIA (CÓDIGO 01, 1B, 04 e 55)
    """
    reg: Literal['C186']
    num_item: CampoInteiro
    cod_item: CampoAlphanumerico
    cst_icms: CampoInteiro
    cfop: CampoInteiro
    cod_mot_rest_compl: CampoAlphanumerico
    quant_conv: CampoDecimal
    unid: CampoAlphanumerico
    cod_mod_entrada: CampoAlphanumerico
    serie_entrada: CampoSerie
    num_doc_entrada: CampoInteiro
    chv_dfe_entrada: CampoInteiro
    dt_doc_entrada: CampoData
    num_item_entrada: CampoInteiro
    vl_unit_conv_entrada: CampoDecimal
    vl_unit_icms_op_conv_entrada: CampoDecimal
    vl_unit_bc_icms_st_conv_entrada: CampoDecimal
    vl_unit_icms_st_conv_entrada: CampoDecimal
    vl_unit_fcp_st_conv_entrada: CampoDecimal

from typing import Literal
from pyspedfiscal.models import Registro
from pyspedfiscal.campos import CampoAlphanumerico, CampoDecimal


class RegistroE115(Registro):
    """ 
    INFORMAÇÕES ADICIONAIS DA APURAÇÃO – VALORES
    DECLARATÓRIOS 
    """

    reg: Literal['E115']
    cod_inf_adic: CampoAlphanumerico
    vl_inf_adic: CampoDecimal
    descr_compl_aj: CampoAlphanumerico

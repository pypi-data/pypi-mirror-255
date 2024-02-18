from typing import Literal
from pyspedfiscal.campos import CampoDecimal, CampoAlphanumerico
from pyspedfiscal.models import Registro


class RegistroC197(Registro):
    """ 
    Outras Obrigações Tributárias, Ajustes e Informações provenientes de
    Documento Fiscal 
    """
    reg: Literal['C197']
    cod_aj: CampoAlphanumerico
    descr_compl_aj: CampoAlphanumerico
    cod_item: CampoAlphanumerico
    vl_bc_icms: CampoDecimal
    aliq_icms: CampoDecimal
    vl_icms: CampoDecimal
    vl_outros: CampoDecimal

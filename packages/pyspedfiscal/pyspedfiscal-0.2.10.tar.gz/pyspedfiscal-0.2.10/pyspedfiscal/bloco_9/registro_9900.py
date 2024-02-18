from typing import Literal
from pyspedfiscal.models import Registro
from pyspedfiscal.campos import CampoInteiro, CampoAlphanumerico


class Registro9900(Registro):
    """ REGISTROS DO ARQUIVO """
    reg: Literal['9900']
    reg_blc: CampoAlphanumerico
    qtd_reg_blc: CampoInteiro

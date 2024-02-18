from typing import Literal
from pyspedfiscal.campos import CampoDecimal, CampoAlphanumerico
from pyspedfiscal.models import Registro


class RegistroC171(Registro):
    """ ARMAZENAMENTO DE COMBUSTÍVEIS (código 01, 55) """
    reg: Literal['C171']
    num_tanque: CampoAlphanumerico
    qtde: CampoDecimal

from typing import Literal
from pyspedfiscal.models import Registro
from pyspedfiscal.campos import CampoAlphanumerico, CampoDecimal


class Registro0220(Registro):
    """ FATORES DE CONVERSÃO DE UNIDADES"""

    reg: Literal['0220']
    unid_conv: CampoAlphanumerico
    fat_conv: CampoDecimal
    cod_barra: CampoAlphanumerico

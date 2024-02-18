from typing import Literal
from pyspedfiscal.models import Registro
from pyspedfiscal.campos import CampoAlphanumerico


class Registro0190(Registro):
    """ IDENTIFICAÇÃO DAS UNIDADES DE MEDIDA """

    reg: Literal['0190']
    unid: CampoAlphanumerico
    descr: CampoAlphanumerico

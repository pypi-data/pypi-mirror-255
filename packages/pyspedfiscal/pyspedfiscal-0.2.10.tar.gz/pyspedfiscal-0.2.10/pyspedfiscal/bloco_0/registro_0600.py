from typing import Literal
from pyspedfiscal.models import Registro
from pyspedfiscal.campos import CampoAlphanumerico, CampoData


class Registro0600(Registro):
    """ CENTRO DE CUSTOS """

    reg: Literal['0600']
    dt_alt: CampoData
    cod_ccus: CampoAlphanumerico
    ccus: CampoAlphanumerico

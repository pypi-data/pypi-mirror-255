from typing import Literal
from pyspedfiscal.models import Registro
from pyspedfiscal.campos import CampoAlphanumerico


class Registro0015(Registro):
    """ Dados do Contribuinte Substituto ou Responsável pelo ICMS Destino """

    reg: Literal['0015']
    uf_st: CampoAlphanumerico
    ie_st: CampoAlphanumerico

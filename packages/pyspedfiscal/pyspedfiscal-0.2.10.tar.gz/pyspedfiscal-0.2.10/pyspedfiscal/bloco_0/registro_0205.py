from typing import Literal
from pyspedfiscal.models import Registro
from pyspedfiscal.campos import CampoAlphanumerico, CampoData


class Registro0205(Registro):
    """ ALTERAÇÃO DO ITEM """

    reg: Literal['0205']
    descr_ant_item: CampoAlphanumerico
    dt_ini: CampoData
    dt_fim: CampoData
    cod_ant_item: CampoAlphanumerico

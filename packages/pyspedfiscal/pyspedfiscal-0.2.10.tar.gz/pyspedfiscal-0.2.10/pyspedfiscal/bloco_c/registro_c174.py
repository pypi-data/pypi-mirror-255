from typing import Literal
from pyspedfiscal.campos import CampoAlphanumerico, CampoEnumerate
from pyspedfiscal.models import Registro


class IndArm(CampoEnumerate):
    """ Indicador do tipo da arma de fogo """
    permitido = '0'
    restrito = '1'


class RegistroC174(Registro):
    """ OPERAÇÕES COM ARMAS DE FOGO (CÓDIGO 01) """
    reg: Literal['C174']
    ind_arm: IndArm
    num_arm: CampoAlphanumerico
    descr_compl: CampoAlphanumerico

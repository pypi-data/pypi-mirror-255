from typing import List, Literal
from pyspedfiscal.models import Registro
from pyspedfiscal.campos import CampoEnumerate
from pydantic import Field

from pyspedfiscal.bloco_c.registro_c100 import RegistroC100


class IndMov(CampoEnumerate):
    """ Indicador de movimento """
    com_movimento = '0'
    sem_movimento = '1'


class RegistroC001(Registro):
    """ ABERTURA DO BLOCO C """
    reg: Literal['C001']
    ind_mov: IndMov

    # Registros filhos nivel 2
    registros_c100: List[RegistroC100] = Field(
        default_factory=list, exclude=True)

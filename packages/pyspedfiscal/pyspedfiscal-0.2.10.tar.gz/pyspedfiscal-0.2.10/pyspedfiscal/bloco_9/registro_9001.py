from typing import Literal
from pyspedfiscal.models import Registro
from pyspedfiscal.campos import CampoEnumerate
from typing import List
from pydantic import Field
from .registro_9900 import Registro9900


class IndMov(CampoEnumerate):
    """ Indicador de movimento """
    com_movimento = '0'
    sem_movimento = '1'


class Registro9001(Registro):
    """ Abertura do Bloco 9"""
    reg: Literal['9001']
    ind_mov: IndMov

    # Registros filhos nivel 2
    registros_9900: List[Registro9900] = Field(
        default_factory=list, exclude=True)

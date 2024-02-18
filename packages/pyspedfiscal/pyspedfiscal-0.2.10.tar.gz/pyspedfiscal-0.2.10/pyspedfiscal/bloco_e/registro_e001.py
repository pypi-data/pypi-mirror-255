from typing import List, Literal
from pyspedfiscal.models import Registro
from pyspedfiscal.campos import CampoEnumerate
from pydantic import Field
from .registro_e100 import RegistroE100


class IndMov(CampoEnumerate):
    """ Indicador de movimento """
    com_movimento = '0'
    sem_movimento = '1'


class RegistroE001(Registro):
    """ ABERTURA DO BLOCO E """
    reg: Literal['E001']
    ind_mov: IndMov

    # Registros filhos nivel 2
    registros_e100: List[RegistroE100] = Field(
        default_factory=list, exclude=True)

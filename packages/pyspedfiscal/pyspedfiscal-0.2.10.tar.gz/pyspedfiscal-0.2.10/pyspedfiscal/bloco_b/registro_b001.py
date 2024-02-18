from ..models import Registro
from typing import Literal

from pydantic import Field
from .registro_b020 import RegistroB020
from .registro_b030 import RegistroB030
from .registro_b350 import RegistroB350
from .registro_b420 import RegistroB420
from .registro_b440 import RegistroB440
from .registro_b460 import RegistroB460
from .registro_b470 import RegistroB470
from .registro_b500 import RegistroB500
from ..campos import CampoEnumerate
from typing import List


class IndDad(CampoEnumerate):
    """ Indicador de movimento """
    com_dados_informados = '0'
    sem_dados_informados = '1'


class RegistroB001(Registro):
    """ ABERTURA DO BLOCO B """
    reg: Literal['B001']
    ind_dad: IndDad

    # Registros filhos nivel 2
    registros_b020: List[RegistroB020] = Field(
        default_factory=list, exclude=True)
    registros_b030: List[RegistroB030] = Field(
        default_factory=list, exclude=True)
    registros_b350: List[RegistroB350] = Field(
        default_factory=list, exclude=True)
    registros_b420: List[RegistroB420] = Field(
        default_factory=list, exclude=True)
    registros_b440: List[RegistroB440] = Field(
        default_factory=list, exclude=True)
    registros_b460: List[RegistroB460] = Field(
        default_factory=list, exclude=True)
    registro_b470: RegistroB470 = Field(
        default=None, exclude=True)
    registro_b500: RegistroB500 = Field(
        default=None, exclude=True)

from typing import Literal
from pyspedfiscal.models import Registro
from pyspedfiscal.campos import CampoEnumerate
from typing import List
from pydantic import Field

from .registro_0002 import Registro0002
from .registro_0005 import Registro0005
from .registro_0015 import Registro0015
from .registro_0100 import Registro0100
from .registro_0150 import Registro0150
from .registro_0190 import Registro0190
from .registro_0200 import Registro0200
from .registro_0300 import Registro0300
from .registro_0400 import Registro0400
from .registro_0450 import Registro0450
from .registro_0460 import Registro0460
from .registro_0500 import Registro0500
from .registro_0600 import Registro0600


class IndMov(CampoEnumerate):
    """ Indicador de movimento """
    com_movimento = '0'
    sem_movimento = '1'


class Registro0001(Registro):
    """ ABERTURA DO BLOCO 0 """

    reg: Literal['0001']
    ind_mov: IndMov

    # Registros filhos nivel 2
    registro_0002: Registro0002 = Field(
        default=None, exclude=True)
    registro_0005: Registro0005 = Field(
        default=None, exclude=True)
    registros_0015: List[Registro0015] = Field(
        default_factory=list, exclude=True)
    registro_0100: Registro0100 = Field(
        default=None, exclude=True)
    registros_0150: List[Registro0150] = Field(
        default_factory=list, exclude=True)
    registros_0190: List[Registro0190] = Field(
        default_factory=list, exclude=True)
    registros_0200: List[Registro0200] = Field(
        default_factory=list, exclude=True)
    registros_0300: List[Registro0300] = Field(
        default_factory=list, exclude=True)
    registros_0400: List[Registro0400] = Field(
        default_factory=list, exclude=True)
    registros_0450: List[Registro0450] = Field(
        default_factory=list, exclude=True)
    registros_0460: List[Registro0460] = Field(
        default_factory=list, exclude=True)
    registros_0500: List[Registro0500] = Field(
        default_factory=list, exclude=True)
    registros_0600: List[Registro0600] = Field(
        default_factory=list, exclude=True)

from typing import List, Literal
from pyspedfiscal.models import Registro
from pyspedfiscal.campos import CampoData
from pydantic import Field
from .registro_e110 import RegistroE110


class RegistroE100(Registro):
    """ PERÍODO DA APURAÇÃO DO ICMS """
    reg: Literal['E100']
    dt_ini: CampoData
    dt_fin: CampoData

    # Registros filhos nivel 3
    registros_e110: List[RegistroE110] = Field(
        default_factory=list, exclude=True)

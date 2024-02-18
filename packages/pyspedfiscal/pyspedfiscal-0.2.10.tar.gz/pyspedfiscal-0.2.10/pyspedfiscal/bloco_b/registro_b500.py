from ..models import Registro
from typing import Literal
from ..campos import CampoInteiro, CampoDecimal
from .registro_b510 import RegistroB510
from pydantic import Field
from typing import List


class RegistroB500(Registro):
    """ APURAÇÃO DO ISS SOCIEDADE UNIPROFISSIONAL """
    reg: Literal['B500']
    vl_rec: CampoDecimal
    qtd_prof: CampoInteiro
    vl_or: CampoDecimal

    # Registros filhos nivel 3
    registros_b510: List[RegistroB510] = Field(
        default_factory=list, exclude=True)

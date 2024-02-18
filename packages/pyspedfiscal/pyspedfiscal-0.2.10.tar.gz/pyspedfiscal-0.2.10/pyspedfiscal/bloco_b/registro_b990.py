from ..models import Registro
from typing import Literal
from ..campos import CampoInteiro


class RegistroB990(Registro):
    """ ENCERRAMENTO DO BLOCO B """
    reg: Literal['B990']
    qtd_lin_b: CampoInteiro

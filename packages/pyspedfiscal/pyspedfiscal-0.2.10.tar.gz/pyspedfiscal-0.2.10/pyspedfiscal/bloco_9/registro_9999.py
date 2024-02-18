from typing import Literal
from pyspedfiscal.models import Registro
from pyspedfiscal.campos import CampoInteiro


class Registro9999(Registro):
    """ Encerramento do Arquivo Digital """
    reg: Literal['9999']
    qtd_lin: CampoInteiro

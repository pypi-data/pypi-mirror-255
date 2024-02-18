from typing import Literal
from pyspedfiscal.models import Registro
from pyspedfiscal.campos import CampoInteiro


class Registro9990(Registro):
    """ Encerramento do Bloco 9 """
    reg: Literal['9990']
    qtd_lin_9: CampoInteiro

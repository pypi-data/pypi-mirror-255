from typing import Literal
from pyspedfiscal.models import Registro
from pyspedfiscal.campos import CampoInteiro


class Registro0990(Registro):
    """  """

    reg: Literal['0990']
    qtd_lin_0: CampoInteiro

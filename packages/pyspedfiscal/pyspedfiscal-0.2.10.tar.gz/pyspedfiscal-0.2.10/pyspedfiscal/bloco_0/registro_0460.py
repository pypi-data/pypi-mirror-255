from typing import Literal
from pyspedfiscal.models import Registro
from pyspedfiscal.campos import CampoAlphanumerico


class Registro0460(Registro):
    """ TABELA DE OBSERVAÇÕES DO LANÇAMENTO FISCAL """

    reg: Literal['0460']
    cod_obs: CampoAlphanumerico
    txt: CampoAlphanumerico

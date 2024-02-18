from typing import Literal
from pyspedfiscal.models import Registro
from pyspedfiscal.campos import CampoAlphanumerico


class Registro0450(Registro):
    """ TABELA DE INFORMAÇÃO COMPLEMENTAR DO DOCUMENTO FISCAL """

    reg: Literal['0450']
    cod_inf: CampoAlphanumerico
    txt: CampoAlphanumerico

from typing import Literal
from pyspedfiscal.models import Registro
from pyspedfiscal.campos import CampoAlphanumerico


class Registro0400(Registro):
    """ TABELA DE NATUREZA DA OPERAÇÃO/PRESTAÇÃO """

    reg: Literal['0400']
    cod_nat: CampoAlphanumerico
    descr_nat: CampoAlphanumerico

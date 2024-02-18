from typing import Literal
from pyspedfiscal.models import Registro
from pyspedfiscal.campos import CampoAlphanumerico


class Registro0206(Registro):
    """ CÓDIGO DE PRODUTO CONFORME TABELA PUBLICADA PELA ANP """

    reg: Literal['0206']
    cod_comb: CampoAlphanumerico

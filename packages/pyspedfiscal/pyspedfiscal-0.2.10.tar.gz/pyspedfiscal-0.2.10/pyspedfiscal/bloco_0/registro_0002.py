from typing import Literal
from pyspedfiscal.models import Registro
from ..tabelas import ClassifContribIpi


class Registro0002(Registro):
    """ Classificação do Estabelecimento Industrial ou Equiparado a Industrial """

    reg: Literal['0002']
    clas_estab_ind: ClassifContribIpi

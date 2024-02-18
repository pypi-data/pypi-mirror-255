from typing import Literal
from pyspedfiscal.models import Registro
from pyspedfiscal.campos import CampoAlphanumerico, CampoDecimal


class Registro0210(Registro):
    """ CONSUMO ESPECÍFICO PADRONIZADO (VÁLIDO ATÉ 31/12/2021) """

    reg: Literal['0210']
    cod_item_comp: CampoAlphanumerico
    qtd_comp: CampoDecimal
    perda: CampoDecimal

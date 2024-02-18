from typing import Literal
from pyspedfiscal.models import Registro
from pyspedfiscal.campos import CampoAlphanumerico, CampoDecimal


class Registro0221(Registro):
    """ CORRELAÇÃO ENTRE CÓDIGOS DE ITENS COMERCIALIZADOS """

    reg: Literal['0221']
    cod_item_atomico: CampoAlphanumerico
    qtd_contida: CampoDecimal

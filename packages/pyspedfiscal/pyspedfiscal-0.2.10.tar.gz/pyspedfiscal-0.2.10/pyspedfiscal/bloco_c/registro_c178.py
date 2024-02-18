from typing import Literal
from pyspedfiscal.campos import CampoDecimal, CampoAlphanumerico
from pyspedfiscal.models import Registro


class RegistroC178(Registro):
    """
    OPERAÇÕES COM PRODUTOS SUJEITOS À TRIBUTAÇÃO DE IPI POR
    UNIDADE OU QUANTIDADE DE PRODUTO
    """
    reg: Literal['C178']
    cl_enq: CampoAlphanumerico
    vl_unid: CampoDecimal
    quant_pad: CampoDecimal

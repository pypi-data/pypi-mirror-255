from typing import Literal
from pyspedfiscal.campos import CampoInteiro, CampoAlphanumerico
from pyspedfiscal.models import Registro


class RegistroC177Antes2019(Registro):
    """
    OPERAÇÕES COM PRODUTOS SUJEITOS A SELO DE CONTROLE IPI
    (VÁLIDO ATÉ 31/12/2018)
    """
    reg: Literal['C177']
    cod_selo_ipi: CampoAlphanumerico
    qt_selo_ipi: CampoInteiro


class RegistroC177(Registro):
    """
    COMPLEMENTO DE ITEM - OUTRAS INFORMAÇÕES (código 01, 55) -
    (VÁLIDO A PARTIR DE 01/01/2019)
    """
    reg: Literal['C177']
    cod_inf_ite: CampoAlphanumerico

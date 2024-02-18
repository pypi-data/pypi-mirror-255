from typing import List, Literal
from pyspedfiscal.campos import CampoAlphanumerico
from pydantic import Field
from pyspedfiscal.models import Registro
from pyspedfiscal.bloco_c.registro_c111 import RegistroC111
from pyspedfiscal.bloco_c.registro_c112 import RegistroC112
from pyspedfiscal.bloco_c.registro_c113 import RegistroC113
from pyspedfiscal.bloco_c.registro_c114 import RegistroC114
from pyspedfiscal.bloco_c.registro_c115 import RegistroC115
from pyspedfiscal.bloco_c.registro_c116 import RegistroC116


class RegistroC110(Registro):
    """
    INFORMAÇÃO COMPLEMENTAR DA NOTA FISCAL (CÓDIGO 01, 1B, 04 e 55)
    """
    reg: Literal['C110']
    cod_inf: CampoAlphanumerico
    txt_compl: CampoAlphanumerico

    registros_c111: List[RegistroC111] = Field(
        default_factory=list, exclude=True)
    registros_c112: List[RegistroC112] = Field(
        default_factory=list, exclude=True)
    registros_c113: List[RegistroC113] = Field(
        default_factory=list, exclude=True)
    registros_c114: List[RegistroC114] = Field(
        default_factory=list, exclude=True)
    registros_c115: List[RegistroC115] = Field(
        default_factory=list, exclude=True)
    registros_c116: List[RegistroC116] = Field(
        default_factory=list, exclude=True)

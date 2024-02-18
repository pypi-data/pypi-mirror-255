from typing import List, Literal
from pyspedfiscal.campos import CampoAlphanumerico
from pyspedfiscal.models import Registro
from pydantic import Field

from pyspedfiscal.bloco_c.registro_c197 import RegistroC197


class RegistroC195(Registro):
    """ 
    Complemento do Registro Analítico - Observações do Lançamento Fiscal
    (código 01, 1B, 04 e 55) 
    """
    reg: Literal['C195']
    cod_obs: CampoAlphanumerico
    txt_compl: CampoAlphanumerico

    registros_c197: List[RegistroC197] = Field(
        default_factory=list, exclude=True)

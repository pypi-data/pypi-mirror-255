from pyspedfiscal.campos import CampoDecimal, CampoInteiro, CampoAlphanumerico
from typing import Literal
from pyspedfiscal.models import Registro
from typing import List
from .registro_c165 import RegistroC165
from pydantic import Field


class RegistroC160(Registro):
    """ VOLUMES TRANSPORTADOS (CÓDIGO 01 E 04) - EXCETO COMBUSTÍVEIS. """
    reg: Literal['C160']
    cod_part: CampoAlphanumerico
    veic_id: CampoAlphanumerico
    qtd_vol: CampoInteiro
    peso_brt: CampoDecimal
    peso_liq: CampoDecimal
    uf_id: CampoAlphanumerico

    # Registros filhos nivel 3
    registros_c165: List[RegistroC165] = Field(default_factory=list, exclude=True)

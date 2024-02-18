from ..campos import CampoDecimal, CampoInteiro, CampoAlphanumerico, CampoEnumerate
from typing import Literal
from ..models import Registro
from typing import List
from .registro_c141 import RegistroC141
from pydantic import Field
from ..gerais import IndEmit


class IndTit(CampoEnumerate):
    """ Indicador do tipo de título de crédito """
    duplicata = '00'
    cheque = '01'
    promiddoria = '02'
    recibo = '03'
    outros = '99'


class RegistroC140(Registro):
    """ FATURA (CÓDIGO 01)  """
    reg: Literal['C140']
    ind_emit: IndEmit
    ind_tit: IndTit
    desc_tit: CampoAlphanumerico
    num_tit: CampoAlphanumerico
    qtd_parc: CampoInteiro
    vl_tit: CampoDecimal

    # Registros filhos nivel 3
    registros_c141: List[RegistroC141] = Field(default_factory=list, exclude=True)

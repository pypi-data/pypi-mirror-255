from typing import Literal
from ..models import Registro
from ..campos import CampoAlphanumerico, CampoEnumerate, CampoInteiro
from typing import List
from .registro_0305 import Registro0305
from pydantic import Field


class IdentMerc(CampoEnumerate):
    """ Identificação do tipo de mercadoria """

    bem = '1'
    componente = '2'


class Registro0300(Registro):
    """ CADASTRO DE BENS OU COMPONENTES DO ATIVO IMOBILIZADO """

    reg: Literal['0300']
    cod_ind_bem: CampoAlphanumerico
    ident_merc: IdentMerc
    descr_item: CampoAlphanumerico
    cod_prnc: CampoAlphanumerico
    cod_cta: CampoAlphanumerico
    nr_parc: CampoInteiro

    registros_0305: List[Registro0305] = Field(
        default_factory=list, exclude=True
    )

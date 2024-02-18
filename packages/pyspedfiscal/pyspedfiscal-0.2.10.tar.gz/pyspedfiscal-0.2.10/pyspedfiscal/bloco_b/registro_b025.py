from ..models import Registro
from typing import Literal
from ..campos import CampoDecimal, CampoAlphanumerico


class RegistroB025(Registro):
    """ DETALHAMENTO POR COMBINAÇÃO DE ALÍQUOTA E ITEM DA LISTA DE SERVIÇOS DA LC 116/2003) """
    reg: Literal['B025']
    vl_cont_p: CampoDecimal
    vl_bc_iss_p: CampoDecimal
    aliq_iss: CampoDecimal
    vl_iss_p: CampoDecimal
    vl_isnt_iss_p: CampoDecimal
    cod_serv: CampoAlphanumerico

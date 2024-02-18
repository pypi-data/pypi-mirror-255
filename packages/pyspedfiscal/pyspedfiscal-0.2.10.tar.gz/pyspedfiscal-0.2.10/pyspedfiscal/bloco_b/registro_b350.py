from ..models import Registro
from typing import Literal
from ..campos import CampoAlphanumerico, CampoInteiro, CampoDecimal


class RegistroB350(Registro):
    """ SERVIÇOS PRESTADOS POR INSTITUIÇÕES FINANCEIRAS """
    reg: Literal['B350']
    cod_ctd: CampoAlphanumerico
    cta_iss: CampoAlphanumerico
    cta_cosif: CampoInteiro
    qtd_ocor: CampoInteiro
    cod_serv: CampoInteiro
    vl_cont: CampoDecimal
    vl_bc_iss: CampoDecimal
    aliq_iss: CampoDecimal
    vl_iss: CampoDecimal
    cod_inf_obs: CampoAlphanumerico

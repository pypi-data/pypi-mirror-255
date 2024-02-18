from ..models import Registro
from typing import Literal
from ..campos import CampoDecimal


class RegistroB470(Registro):
    """ APURAÇÃO DO ISS """
    reg: Literal['B470']
    vl_cont: CampoDecimal
    vl_mat_terc: CampoDecimal
    vl_mat_prop: CampoDecimal
    vl_sub: CampoDecimal
    vl_isnt: CampoDecimal
    vl_ded_bc: CampoDecimal
    vl_bc_iss: CampoDecimal
    vl_bc_iss_rt: CampoDecimal
    vl_iss: CampoDecimal
    vl_iss_rt: CampoDecimal
    vl_ded: CampoDecimal
    vl_iss_rec: CampoDecimal
    vl_iss_st: CampoDecimal
    vl_iss_rec_uni: CampoDecimal

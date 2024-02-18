from typing import Literal
from pyspedfiscal.campos import CampoDecimal
from pyspedfiscal.models import Registro


class RegistroC179(Registro):
    """ INFORMAÇÕES COMPLEMENTARES ST (CÓDIGO 01) """
    reg: Literal['C179']
    bc_st_orig_dest: CampoDecimal
    icms_st_rep: CampoDecimal
    icms_st_compl: CampoDecimal
    bc_ret: CampoDecimal
    icms_ret: CampoDecimal

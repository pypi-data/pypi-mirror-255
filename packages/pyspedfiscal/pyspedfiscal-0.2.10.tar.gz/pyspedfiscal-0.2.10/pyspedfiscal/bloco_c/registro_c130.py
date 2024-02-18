from pyspedfiscal.campos import CampoDecimal
from typing import Literal
from pyspedfiscal.models import Registro


class RegistroC130(Registro):
    """ ISSQN, IRRF E PREVIDÊNCIA SOCIAL """
    reg: Literal['C130']
    vl_serv_nt: CampoDecimal
    vl_bc_issqn: CampoDecimal
    vl_issqn: CampoDecimal
    vl_bc_irrf: CampoDecimal
    vl_irrf: CampoDecimal
    vl_bc_prev: CampoDecimal
    vl_prev: CampoDecimal

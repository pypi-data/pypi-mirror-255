from typing import Literal
from pyspedfiscal.campos import CampoDecimal
from pyspedfiscal.models import Registro


class RegistroC172(Registro):
    """ OPERAÇÕES COM ISSQN (CÓDIGO 01)  """
    reg: Literal['172']
    vl_bc_issqn: CampoDecimal
    aliq_issqn: CampoDecimal
    vl_issqn: CampoDecimal

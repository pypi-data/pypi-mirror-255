from pyspedfiscal.campos import CampoDecimal, CampoInteiro, CampoData
from typing import Literal
from pyspedfiscal.models import Registro


class RegistroC141(Registro):
    """ VENCIMENTO DA FATURA (CÓDIGO 01) """
    reg: Literal['C141']
    num_parc: CampoInteiro
    dt_vcto: CampoData
    vl_parc: CampoDecimal

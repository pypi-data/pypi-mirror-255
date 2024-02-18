from typing import Literal
from pyspedfiscal.models import Registro
from pyspedfiscal.campos import CampoAlphanumerico, CampoInteiro


class Registro0305(Registro):
    """ INFORMAÇÃO SOBRE A UTILIZAÇÃO DO BEM """

    reg: Literal['0305']
    cod_ccus: CampoAlphanumerico
    func: CampoAlphanumerico
    vida_util: CampoInteiro

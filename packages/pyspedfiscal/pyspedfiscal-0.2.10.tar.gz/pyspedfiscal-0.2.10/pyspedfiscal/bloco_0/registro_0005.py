from typing import Literal
from pyspedfiscal.models import Registro
from pyspedfiscal.campos import CampoAlphanumerico, CampoInteiro


class Registro0005(Registro):
    """ Dados Complementares da entidade """

    reg: Literal['0005']
    fantasia: CampoAlphanumerico
    cep: CampoInteiro
    end: CampoAlphanumerico
    num: CampoAlphanumerico
    compl: CampoAlphanumerico
    bairro: CampoAlphanumerico
    fone: CampoAlphanumerico
    fax: CampoAlphanumerico
    email: CampoAlphanumerico

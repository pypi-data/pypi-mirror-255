from typing import Literal
from pyspedfiscal.models import Registro
from pyspedfiscal.campos import CampoAlphanumerico, CampoData


class Registro0175(Registro):
    """ Alteração da Tabela de Cadastro de Participante  """

    reg: Literal['0175']
    dt_alt: CampoData
    nr_campo: CampoAlphanumerico
    cont_ant: CampoAlphanumerico

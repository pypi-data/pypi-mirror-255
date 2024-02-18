from typing import Literal
from pyspedfiscal.models import Registro
from pyspedfiscal.campos import CampoAlphanumerico, CampoInteiro
from typing import List
from .registro_0175 import Registro0175
from pydantic import Field


class Registro0150(Registro):
    """ Tabela de Cadastro do Participante """

    reg: Literal['0150']
    cod_part: CampoAlphanumerico
    nome: CampoAlphanumerico
    cod_pais: CampoInteiro
    cnpj: CampoInteiro
    cpf: CampoInteiro
    ie: CampoAlphanumerico
    cod_mun: CampoInteiro
    suframa: CampoAlphanumerico
    end: CampoAlphanumerico
    num: CampoAlphanumerico
    compl: CampoAlphanumerico
    bairro: CampoAlphanumerico

    # Registros filhos nivel 3
    registros_0175: List[Registro0175] = Field(
        default_factory=list, exclude=True)

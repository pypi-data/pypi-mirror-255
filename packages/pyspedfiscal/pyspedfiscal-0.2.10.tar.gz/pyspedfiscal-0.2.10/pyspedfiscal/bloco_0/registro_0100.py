from typing import Literal
from pyspedfiscal.models import Registro
from pyspedfiscal.campos import CampoAlphanumerico, CampoInteiro


class Registro0100(Registro):
    """ Dados do Contabilista """

    reg: Literal['0100']
    nome: CampoAlphanumerico
    cpf: CampoInteiro
    crc: CampoAlphanumerico
    cnpj: CampoInteiro
    cep: CampoInteiro
    end: CampoAlphanumerico
    num: CampoAlphanumerico
    compl: CampoAlphanumerico
    bairro: CampoAlphanumerico
    fone: CampoAlphanumerico
    fax: CampoAlphanumerico
    email: CampoAlphanumerico
    cod_mun: CampoInteiro

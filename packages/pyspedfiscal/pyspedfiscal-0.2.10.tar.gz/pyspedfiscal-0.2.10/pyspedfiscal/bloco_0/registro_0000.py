from typing import Literal
from pyspedfiscal.models import Registro
from pyspedfiscal.campos import CampoEnumerate, CampoData, CampoAlphanumerico, CampoInteiro, CampoCNPJ, CampoCPF
from pyspedfiscal.tabelas import CodVer


class CodFin(CampoEnumerate):
    original = '0'
    substituto = '1'


class IndAtiv(CampoEnumerate):
    industrial = '0'
    outros = '1'


class Registro0000(Registro):
    """ Abertura do Arquivo Digital """

    reg: Literal['0000']
    cod_ver: CodVer
    cod_fin: CodFin
    dt_ini: CampoData
    dt_fin: CampoData
    nome: CampoAlphanumerico
    cnpj: CampoCNPJ
    cpf: CampoCPF
    uf: CampoAlphanumerico
    ie: CampoAlphanumerico
    cod_mun: CampoInteiro
    im: CampoAlphanumerico
    suframa: CampoAlphanumerico
    ind_perfil: CampoAlphanumerico
    ind_ativ: IndAtiv

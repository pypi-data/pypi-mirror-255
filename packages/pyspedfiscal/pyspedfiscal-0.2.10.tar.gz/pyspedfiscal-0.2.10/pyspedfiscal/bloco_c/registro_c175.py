from typing import Literal
from pyspedfiscal.campos import CampoCNPJ, CampoAlphanumerico, CampoEnumerate
from pyspedfiscal.models import Registro


class IndVeicOper(CampoEnumerate):
    """ Indicador do tipo de operação com veículo """
    venda_para_concessionaria = '0'
    faturamento_direto = '1'
    venda_direta = '2'
    venda_da_concessionaria = '3'
    outros = '9'


class RegistroC175(Registro):
    """ OPERAÇÕES COM VEÍCULOS NOVOS (CÓDIGO 01 e 55) """
    reg: Literal['C175']
    ind_veic_oper: IndVeicOper
    cnpj: CampoCNPJ
    uf: CampoAlphanumerico
    chassi_veic: CampoAlphanumerico

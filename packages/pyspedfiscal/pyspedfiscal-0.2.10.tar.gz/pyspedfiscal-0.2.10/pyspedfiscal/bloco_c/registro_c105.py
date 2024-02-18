from typing import Literal
from pyspedfiscal.campos import CampoAlphanumerico, CampoEnumerate
from pyspedfiscal.models import Registro


class Oper(CampoEnumerate):
    """Indicador do tipo de operação"""
    combustiveis_lubrificantes = '0'
    leasing_veiculos_faturamento_direto = '1'


class RegistroC105(Registro):
    """
    OPERAÇÕES COM ICMS ST RECOLHIDO PARA UF DIVERSA DO
    DESTINATÁRIO DO DOCUMENTO FISCAL (CÓDIGO 55)
    """
    reg: Literal['C105']
    oper: Oper
    uf: CampoAlphanumerico

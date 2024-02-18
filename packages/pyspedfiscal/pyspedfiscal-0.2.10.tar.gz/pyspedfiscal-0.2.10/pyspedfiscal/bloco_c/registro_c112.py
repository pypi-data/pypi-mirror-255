from typing import Literal
from pyspedfiscal.campos import CampoAlphanumerico, CampoEnumerate, CampoDecimal, CampoData
from pyspedfiscal.models import Registro


class CodDA(CampoEnumerate):
    """Código do modelo do documento de arrecadação"""
    documento_estadual = '0'
    gnre = '1'


class RegistroC112(Registro):
    """DOCUMENTO DE ARRECADAÇÃO REFERENCIADO"""
    reg: Literal['C112']
    cod_da: CodDA
    uf: CampoAlphanumerico
    num_da: CampoAlphanumerico
    cod_aut: CampoAlphanumerico
    vl_da: CampoDecimal
    dt_vcto: CampoData
    dt_pgto: CampoData

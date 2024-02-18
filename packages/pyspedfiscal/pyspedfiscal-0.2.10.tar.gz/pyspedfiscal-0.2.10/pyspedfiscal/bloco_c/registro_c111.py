from typing import Literal
from pyspedfiscal.campos import CampoAlphanumerico, CampoEnumerate
from pyspedfiscal.models import Registro


class IndProc(CampoEnumerate):
    """Indicador da origem do processo"""
    sefaz = '0'
    justica_federal = '1'
    justica_estadual = '2'
    secex_srf = '3'
    outros = '9'


class RegistroC111(Registro):
    """PROCESSO REFERENCIADO"""
    reg: Literal['C111']
    num_proc: CampoAlphanumerico
    ind_proc: IndProc

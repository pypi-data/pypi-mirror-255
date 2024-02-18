from typing import Literal
from ..campos import CampoAlphanumerico, CampoEnumerate, CampoSerie, CampoInteiro, CampoData, CampoChaveAcesso
from ..tabelas import CodMod
from ..models import Registro
from ..gerais import IndEmit


class IndOper(CampoEnumerate):
    """ Indicador do tipo de operação """
    entrada = '0'
    saida = '1'


class RegistroC113(Registro):
    """DOCUMENTO FISCAL REFERENCIADO"""
    reg: Literal['C113']
    ind_oper: IndOper
    ind_emit: IndEmit
    cod_part: CampoAlphanumerico
    cod_mod: CodMod
    ser: CampoSerie
    sub: CampoInteiro
    num_doc: CampoInteiro
    dt_doc: CampoData
    chv_doce: CampoChaveAcesso

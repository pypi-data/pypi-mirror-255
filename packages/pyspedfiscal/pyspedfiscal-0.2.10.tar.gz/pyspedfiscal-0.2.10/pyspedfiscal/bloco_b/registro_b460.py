from ..models import Registro
from typing import Literal
from ..campos import CampoAlphanumerico, CampoEnumerate, CampoDecimal


class IndDed(CampoEnumerate):
    """ Indicador do tipo de dedução """
    calculo_maior = '0'
    insentivo_cultura = '1'
    decisao_adm_judic = '2'
    outros = '9'


class IndProc(CampoEnumerate):
    """ Indicador da origem do processo """
    sefin = '0'
    justica_federal = '1'
    justica_estadual = '2'
    outros = '9'


class RegistroB460(Registro):
    """ DEDUÇÕES DO ISS """

    reg: Literal['B460']
    ind_ded: IndDed
    vl_ded: CampoDecimal
    num_proc: CampoAlphanumerico
    ind_proc: IndProc
    proc: CampoAlphanumerico
    cod_inf_obs: CampoAlphanumerico
    ind_obr: CampoAlphanumerico

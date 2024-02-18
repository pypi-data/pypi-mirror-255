from ..models import Registro
from typing import Literal
from ..campos import CampoAlphanumerico, CampoEnumerate, CampoInteiro, CampoData, CampoDecimal, CampoSerie
from .registro_b025 import RegistroB025
from pydantic import Field
from typing import List
from ..tabelas import CodModIss, CodSit
from ..gerais import IndEmit


class IndOper(CampoEnumerate):
    """ Indicador do tipo de operação """
    aquisicao = '0'
    prestacao = '1'


class RegistroB020(Registro):
    """
    NOTA FISCAL (CÓDIGO 01), NOTA FISCAL DE SERVIÇOS (CÓDIGO 03),
    NOTA FISCAL DE SERVIÇOS AVULSA (CÓDIGO 3B), NOTA FISCAL DE PRODUTOR
    (CÓDIGO 04), CONHECIMENTO DE TRANSPORTE RODOVIÁRIO DE CARGAS (CÓDIGO
    08), NF-e (CÓDIGO 55), NFC-e (CÓDIGO 65) e NF3-e (CÓDIGO 66).
    """
    reg: Literal['B020']
    ind_oper: IndOper
    ind_emit: IndEmit
    cod_part: CampoAlphanumerico
    cod_mod: CodModIss
    cod_sit: CodSit
    ser: CampoSerie
    num_doc: CampoInteiro
    chv_nfe: CampoInteiro
    dt_doc: CampoData
    cod_mun_serv: CampoAlphanumerico
    vl_cont: CampoDecimal
    vl_mat_terc: CampoDecimal
    vl_sub: CampoDecimal
    vl_isnt_iss: CampoDecimal
    vl_ded_bc: CampoDecimal
    vl_bc_iss: CampoDecimal
    vl_bc_iss_rt: CampoDecimal
    vl_iss_rt: CampoDecimal
    vl_iss: CampoDecimal
    cod_inf_obs: CampoAlphanumerico

    # Registros filhos nivel 3
    registros_b250: List[RegistroB025] = Field(
        default_factory=list, exclude=True)

from ..models import Registro
from typing import Literal
from ..campos import CampoAlphanumerico, CampoInteiro, CampoSerie, CampoData, CampoDecimal
from .registro_b035 import RegistroB035
from pydantic import Field
from typing import List
from ..tabelas import CodModIss


class RegistroB030(Registro):
    """  NOTA FISCAL DE SERVIÇOS SIMPLIFICADA (CÓDIGO 3A) """
    reg: Literal['B030']
    cod_mod: CodModIss
    ser: CampoSerie
    num_doc_ini: CampoInteiro
    num_doc_fin: CampoInteiro
    dt_doc: CampoData
    qtd_canc: CampoInteiro
    vl_cont: CampoDecimal
    vl_isnt_iss: CampoDecimal
    vl_bc_iss: CampoDecimal
    vl_iss: CampoDecimal
    cod_inf_obs: CampoAlphanumerico

    # Registros filhos nivel 3
    registros_b035: List[RegistroB035] = Field(
        default_factory=list, exclude=True)

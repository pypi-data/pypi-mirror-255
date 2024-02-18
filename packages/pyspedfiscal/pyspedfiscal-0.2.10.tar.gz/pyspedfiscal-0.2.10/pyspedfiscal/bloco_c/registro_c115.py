from typing import Literal
from pyspedfiscal.campos import CampoAlphanumerico, CampoEnumerate, CampoCPF, CampoCNPJ, CampoInteiro
from pyspedfiscal.models import Registro


class IndCarga(CampoEnumerate):
    rodoviario = '0'
    ferroviario = '1'
    rodo_ferroviario = '2'
    aquaviario = '3'
    dutoviario = '4'
    aereo = '5'
    outros = '9'


class RegistroC115(Registro):
    """LOCAL DA COLETA E/OU ENTREGA (CÓDIGO 01, 1B E 04)"""
    reg: Literal['C115']
    ind_carga: IndCarga
    cnpj_col: CampoCNPJ
    ie_col: CampoAlphanumerico
    cpf_col: CampoCPF
    cod_mun_col: CampoInteiro
    cnpj_entg: CampoCNPJ
    ie_entg: CampoAlphanumerico
    cpf_entg: CampoCPF
    cod_mun_entg: CampoInteiro

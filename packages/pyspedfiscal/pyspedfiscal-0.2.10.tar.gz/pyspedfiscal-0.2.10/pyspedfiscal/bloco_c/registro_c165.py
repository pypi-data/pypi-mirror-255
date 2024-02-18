from typing import Literal
from pyspedfiscal.campos import CampoDecimal, CampoInteiro, CampoAlphanumerico, CampoCPF
from pyspedfiscal.models import Registro


class RegistroC165(Registro):
    """ OPERAÇÕES COM COMBUSTÍVEIS (CÓDIGO 01) """
    reg: Literal['C165']
    cod_part: CampoAlphanumerico
    veic_id: CampoAlphanumerico
    cod_aut: CampoAlphanumerico
    nr_passe: CampoAlphanumerico
    hora: CampoAlphanumerico
    temper: CampoDecimal
    qtd_vol: CampoInteiro
    peso_brt: CampoDecimal
    peso_liq: CampoDecimal
    nom_mot: CampoAlphanumerico
    cpf: CampoCPF
    uf_id: CampoAlphanumerico

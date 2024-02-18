from typing import Literal
from pyspedfiscal.campos import CampoAlphanumerico, CampoInteiro, CampoData
from pyspedfiscal.models import Registro
from pyspedfiscal.tabelas import CodMod


class RegistroC114(Registro):
    """CUPOM FISCAL REFERENCIADO"""
    reg: Literal['C114']
    cod_mod: CodMod
    ecf_fab: CampoAlphanumerico
    ecf_cx: CampoInteiro
    num_doc: CampoInteiro
    dt_doc: CampoData

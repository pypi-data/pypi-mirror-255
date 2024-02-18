from typing import Literal
from pyspedfiscal.campos import CampoData, CampoInteiro, CampoChaveAcesso
from pyspedfiscal.models import Registro
from pyspedfiscal.tabelas import CodMod


class RegistroC116(Registro):
    """CUPOM FISCAL ELETRÔNICO REFERENCIADO"""
    reg: Literal['C116']
    cod_mod: CodMod
    nr_sat: CampoInteiro
    chv_cfe: CampoChaveAcesso
    num_cfe: CampoInteiro
    dt_doc: CampoData

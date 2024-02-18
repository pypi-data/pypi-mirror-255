from typing import Literal
from pyspedfiscal.campos import CampoDecimal
from pyspedfiscal.models import Registro


class RegistroC101(Registro):
    """
    INFORMAÇÃO COMPLEMENTAR DOS DOCUMENTOS FISCAIS
    QUANDO DAS OPERAÇÕES INTERESTADUAIS DESTINADAS A CONSUMIDOR FINAL
    NÃO CONTRIBUINTE EC 87/15 (CÓDIGO 55)
    """
    reg: Literal['C101']
    vl_fcp_uf_dest: CampoDecimal
    vl_icms_uf_dest: CampoDecimal
    vl_icms_uf_rem: CampoDecimal

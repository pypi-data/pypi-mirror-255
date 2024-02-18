from typing import Literal
from pyspedfiscal.models import Registro
from pyspedfiscal.campos import CampoAlphanumerico, CampoInteiro, CampoEnumerate, CampoData


class CodigoNatCC(CampoEnumerate):
    """ Código da natureza da conta/grupo de contas """
    passivo = '01'
    ativo = '02'
    patrimonio_liquido = '03'
    contas_resultado = '04'
    contas_compensacao = '05'
    outras = '09'


class IndCTA(CampoEnumerate):
    """ Indicador do tipo de conta """
    analitica = 'A'
    sintetica = 'S'


class Registro0500(Registro):
    """ PLANO DE CONTAS CONTÁBEIS """

    reg: Literal['0500']
    dt_alt: CampoData
    cod_nat_cc: CodigoNatCC
    ind_cta: IndCTA
    nivel: CampoInteiro
    cod_cta: CampoAlphanumerico
    nome_cta: CampoAlphanumerico

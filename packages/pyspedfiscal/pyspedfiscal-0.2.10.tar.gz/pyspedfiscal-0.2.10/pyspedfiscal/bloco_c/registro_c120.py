from pyspedfiscal.campos import CampoDecimal, CampoAlphanumerico, CampoEnumerate
from typing import Literal
from pyspedfiscal.models import Registro


class CodDocImp(CampoEnumerate):
    """ Documento de importação """
    declaracao_importacao = '0'
    declaracao_simplificada = '1'


class RegistroC120(Registro):
    """ COMPLEMENTO DE DOCUMENTO - OPERAÇÕES DE IMPORTAÇÃO (CÓDIGOS 01 e 55) """
    reg: Literal['C120']
    cod_doc_imp: CodDocImp
    num_doc_imp: CampoAlphanumerico
    pis_imp: CampoDecimal
    cofins_imp: CampoDecimal
    num_acdraw: CampoAlphanumerico

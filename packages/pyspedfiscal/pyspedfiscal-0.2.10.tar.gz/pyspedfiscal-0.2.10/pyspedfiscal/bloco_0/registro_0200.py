from typing import Literal
from typing import List
from pydantic import Field
from ..models import Registro
from ..campos import CampoEnumerate, CampoAlphanumerico, CampoDecimal, CampoInteiro
from .registro_0205 import Registro0205
from .registro_0206 import Registro0206
from .registro_0210 import Registro0210
from .registro_0220 import Registro0220
from .registro_0221 import Registro0221


class TipoItem(CampoEnumerate):
    revenda = '00'
    materia_prima = '01'
    embalagem = '02'
    produto_em_processo = '03'
    produto_acabado = '04'
    subproduto = '05'
    produto_intermediario = '06'
    uso_e_consumo = '07'
    imobilizado = '08'
    servico = '09'
    outros_insumos = '10'
    outras = '99'


class Registro0200(Registro):
    """ TABELA DE IDENTIFICAÇÃO DO ITEM (PRODUTO E SERVIÇOS) """

    reg: Literal['0200']
    cod_item: CampoAlphanumerico
    descr_item: CampoAlphanumerico
    cod_barra: CampoAlphanumerico
    cod_ant_item: CampoAlphanumerico
    unid_inv: CampoAlphanumerico
    tipo_item: TipoItem
    cod_ncm: CampoAlphanumerico
    ex_ipi: CampoAlphanumerico
    cod_gen: CampoAlphanumerico  # TODO: Tabela 4.2.1.
    # TODO: Anexo I da Lei Complementar Federal nº 116/03.
    cod_lst: CampoAlphanumerico
    aliq_icms: CampoDecimal
    cest: CampoInteiro

    # Registros filhos nivel 3
    registros_0205: List[Registro0205] = Field(
        default_factory=list, exclude=True)
    registros_0206: List[Registro0206] = Field(
        default_factory=list, exclude=True)
    registros_0210: List[Registro0210] = Field(
        default_factory=list, exclude=True)
    registros_0220: List[Registro0220] = Field(
        default_factory=list, exclude=True)
    registros_0221: List[Registro0221] = Field(
        default_factory=list, exclude=True)

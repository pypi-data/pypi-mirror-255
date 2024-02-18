from ..models import Registro
from typing import Literal
from ..campos import CampoAlphanumerico, CampoEnumerate, CampoCPF


class IndProf(CampoEnumerate):
    """ Indicador de habilitação """
    habilitado = '0'
    nao_habilitado = '1'


class IndEsc(CampoEnumerate):
    """ Indicador de escolaridade """
    superior = '0'
    medio = '1'


class IndSoc(CampoEnumerate):
    """ Indicador de participação societária """
    socio = '0'
    nao_socio = '1'


class RegistroB510(Registro):
    """ UNIPROFISSIONAL - EMPREGADOS E SÓCIOS """
    reg: Literal['B510']
    ind_prof: IndProf
    ind_esc: IndEsc
    ind_soc: IndSoc
    cpf: CampoCPF
    nome: CampoAlphanumerico

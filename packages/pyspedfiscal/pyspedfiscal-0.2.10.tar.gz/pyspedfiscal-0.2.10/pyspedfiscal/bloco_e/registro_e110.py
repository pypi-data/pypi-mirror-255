from typing import List, Literal
from pyspedfiscal.models import Registro
from pyspedfiscal.campos import CampoDecimal
from pydantic import Field
from .registro_e115 import RegistroE115


class RegistroE110(Registro):
    """ APURAÇÃO DO ICMS – OPERAÇÕES PRÓPRIAS """

    reg: Literal['E110']
    vl_tot_debitos: CampoDecimal
    vl_aj_debitos: CampoDecimal
    vl_tot_aj_debitos: CampoDecimal
    vl_estornos_cred: CampoDecimal
    vl_tot_creditos: CampoDecimal
    vl_aj_creditos: CampoDecimal
    vl_tot_aj_creditos: CampoDecimal
    vl_estornos_deb: CampoDecimal
    vl_sld_credor_ant: CampoDecimal
    vl_sld_apurado: CampoDecimal
    vl_tot_ded: CampoDecimal
    vl_icms_recolher: CampoDecimal
    vl_sld_credor_transportar: CampoDecimal
    deb_esp: CampoDecimal

    # Registros filhos nivel 4
    registros_c115: List[RegistroE115] = Field(
        default_factory=list, exclude=True)

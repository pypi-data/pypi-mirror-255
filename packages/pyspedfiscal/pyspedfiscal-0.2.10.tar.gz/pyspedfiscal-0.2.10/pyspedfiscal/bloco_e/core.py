from typing import List
from ..models import Bloco
from .registro_e001 import RegistroE001
from .registro_e100 import RegistroE100
from .registro_e110 import RegistroE110
from .registro_e115 import RegistroE115


class BlocoE(Bloco):
    def __init__(self):
        self.registro_e001: RegistroE001 = None

    @classmethod
    def ler_registros(cls, registros: List[str]) -> 'BlocoE':
        bloco = cls()

        for registro in registros:
            tipo_registro = registro[1:5].upper()

            # Nivel 1 - Registro Pai
            if tipo_registro == 'E001':
                bloco.registro_e001 = RegistroE001.ler_registro(registro)

            # Nivel 2 - Filho de E001
            if tipo_registro == 'E100':
                bloco.registro_e001.registros_e100.append(
                    RegistroE100.ler_registro(registro)
                )

            # Nivel 3 - Filho de E100
            if tipo_registro == 'E110':
                bloco.registro_e001.registros_e100[-1].registros_e110.append(
                    RegistroE110.ler_registro(registro)
                )

            # Nivel 4 - Filho de E110
            if tipo_registro == 'E115':
                bloco.registro_e001.registros_e100[-1].registros_e110[-1].registros_c115.append(
                    RegistroE115.ler_registro(registro)
                )

        return bloco

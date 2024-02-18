from typing import List
from ..models import Bloco
from .registro_b001 import RegistroB001
from .registro_b020 import RegistroB020
from .registro_b025 import RegistroB025
from .registro_b030 import RegistroB030
from .registro_b035 import RegistroB035
from .registro_b350 import RegistroB350
from .registro_b420 import RegistroB420
from .registro_b440 import RegistroB440
from .registro_b460 import RegistroB460
from .registro_b470 import RegistroB470
from .registro_b500 import RegistroB500
from .registro_b510 import RegistroB510
from .registro_b990 import RegistroB990


class BlocoB(Bloco):
    def __init__(self):
        self.registro_b001: RegistroB001 = None
        self.registro_b990: RegistroB990 = None

    @classmethod
    def ler_registros(cls, registros: List[str]) -> 'BlocoB':
        bloco = cls()

        for registro in registros:
            tipo_registro = registro[1:5].upper()

            # Nivel 1 - Registro Pai
            if tipo_registro == 'B001':
                bloco.registro_b001 = RegistroB001.ler_registro(registro)

            # Nivel 2 - Filho de B001
            if tipo_registro == 'B020':
                bloco.registro_b001.registros_b020.append(RegistroB020.ler_registro(registro))

            # Nivel 3 - Filho de B020
            if tipo_registro == 'B025':
                bloco.registro_b001.registros_b020[-1].registros_b250.append(RegistroB025.ler_registro(registro))

            # Nivel 2 - Filho de B001
            if tipo_registro == 'B030':
                bloco.registro_b001.registros_b030.append(RegistroB030.ler_registro(registro))

            # Nivel 3 - Filho de B030
            if tipo_registro == 'B035':
                bloco.registro_b001.registros_b030[-1].registros_b035.append(RegistroB035.ler_registro(registro))

            # Nivel 2 - Filho de B001
            if tipo_registro == 'B350':
                bloco.registro_b001.registros_b350.append(RegistroB350.ler_registro(registro))

            # Nivel 2 - Filho de B001
            if tipo_registro == 'B420':
                bloco.registro_b001.registros_b420.append(RegistroB420.ler_registro(registro))

            # Nivel 2 - Filho de B001
            if tipo_registro == 'B440':
                bloco.registro_b001.registros_b440.append(RegistroB440.ler_registro(registro))

            # Nivel 2 - Filho de B001
            if tipo_registro == 'B460':
                bloco.registro_b001.registros_b460.append(RegistroB460.ler_registro(registro))

            # Nivel 2 - Filho de B001
            if tipo_registro == 'B470':
                bloco.registro_b001.registro_b470 = RegistroB470.ler_registro(registro)

            # Nivel 2 - Filho de B001
            if tipo_registro == 'B500':
                bloco.registro_b001.registro_b500 = RegistroB500.ler_registro(registro)

            # Nivel 3 - Filho de B500
            if tipo_registro == 'B510':
                bloco.registro_b001.registro_b500.registros_b510.append(RegistroB510.ler_registro(registro))

            # Nivel 1 - Registro Pai
            if tipo_registro == 'B990':
                bloco.registro_b990 = RegistroB990.ler_registro(registro)

        return bloco

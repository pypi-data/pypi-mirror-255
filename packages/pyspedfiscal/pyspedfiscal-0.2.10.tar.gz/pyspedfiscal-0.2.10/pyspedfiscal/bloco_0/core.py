from typing import List
from ..models import Bloco
from .registro_0000 import Registro0000
from .registro_0001 import Registro0001
from .registro_0002 import Registro0002
from .registro_0005 import Registro0005
from .registro_0015 import Registro0015
from .registro_0100 import Registro0100
from .registro_0150 import Registro0150
from .registro_0175 import Registro0175
from .registro_0190 import Registro0190
from .registro_0200 import Registro0200
from .registro_0205 import Registro0205
from .registro_0206 import Registro0206
from .registro_0210 import Registro0210
from .registro_0220 import Registro0220
from .registro_0221 import Registro0221
from .registro_0300 import Registro0300
from .registro_0305 import Registro0305
from .registro_0400 import Registro0400
from .registro_0450 import Registro0450
from .registro_0460 import Registro0460
from .registro_0500 import Registro0500
from .registro_0600 import Registro0600
from .registro_0990 import Registro0990


class Bloco0(Bloco):
    def __init__(self):
        self.registro_0000: Registro0000 = None
        self.registro_0001: Registro0001 = None
        self.registro_0990: Registro0990 = None

    @classmethod
    def ler_registros(cls, registros: List[str]) -> 'Bloco0':
        bloco = cls()

        for registro in registros:
            tipo_registro = registro[1:5].upper()

            # Nivel 0 - Abertura do Arquivo Digital
            if tipo_registro == '0000':
                bloco.registro_0000 = Registro0000.ler_registro(registro)

            # Nivel 1 - Registro Pai
            if tipo_registro == '0001':
                bloco.registro_0001 = Registro0001.ler_registro(registro)

            # Nivel 2 - Filho de 0001
            if tipo_registro == '0002':
                bloco.registro_0001.registro_0002 = Registro0002.ler_registro(registro)

            # Nivel 2 - Filho de 0001
            if tipo_registro == '0005':
                bloco.registro_0001.registro_0005 = Registro0005.ler_registro(registro)

            # Nivel 2 - Filho de 0001
            if tipo_registro == '0015':
                bloco.registro_0001.registros_0015.append(Registro0015.ler_registro(registro))

            # Nivel 2 - Filho de 0001
            if tipo_registro == '0100':
                bloco.registro_0001.registro_0100 = Registro0100.ler_registro(registro)

            # Nivel 2 - Filho de 0001
            if tipo_registro == '0150':
                bloco.registro_0001.registros_0150.append(Registro0150.ler_registro(registro))

            # Nivel 3 - Filho de 0150
            if tipo_registro == '0175':
                bloco.registro_0001.registros_0150[-1].registros_0175.append(
                    Registro0175.ler_registro(registro)
                )

            # Nivel 2 - Filho de 0001
            if tipo_registro == '0190':
                bloco.registro_0001.registros_0190.append(
                    Registro0190.ler_registro(registro)
                )

            # Nivel 2 - Filho de 0001
            if tipo_registro == '0200':
                bloco.registro_0001.registros_0200.append(
                    Registro0200.ler_registro(registro)
                )

            # Nivel 3 - Filho de 0200
            if tipo_registro == '0205':
                bloco.registro_0001.registros_0200[-1].registros_0205.append(
                    Registro0205.ler_registro(registro)
                )

            # Nivel 3 - Filho de 0200
            if tipo_registro == '0206':
                bloco.registro_0001.registros_0200[-1].registros_0206.append(
                    Registro0206.ler_registro(registro)
                )

            # Nivel 3 - Filho de 0200
            if tipo_registro == '0210':
                bloco.registro_0001.registros_0200[-1].registros_0210.append(
                    Registro0210.ler_registro(registro)
                )

            # Nivel 3 - Filho de 0200
            if tipo_registro == '0220':
                bloco.registro_0001.registros_0200[-1].registros_0220.append(
                    Registro0220.ler_registro(registro)
                )

            # Nivel 3 - Filho de 0200
            if tipo_registro == '0221':
                bloco.registro_0001.registros_0200[-1].registros_0221.append(
                    Registro0221.ler_registro(registro)
                )

            # Nivel 2 - Filho de 0001
            if tipo_registro == '0300':
                bloco.registro_0001.registros_0300.append(
                    Registro0300.ler_registro(registro)
                )

            # Nivel 3 - Filho de 0300
            if tipo_registro == '0305':
                bloco.registro_0001.registros_0300[-1].registros_0305.append(
                    Registro0305.ler_registro(registro)
                )

            # Nivel 2 - Filho de 0001
            if tipo_registro == '0400':
                bloco.registro_0001.registros_0400.append(
                    Registro0400.ler_registro(registro)
                )

            # Nivel 2 - Filho de 0001
            if tipo_registro == '0450':
                bloco.registro_0001.registros_0450.append(
                    Registro0450.ler_registro(registro)
                )

            # Nivel 2 - Filho de 0001
            if tipo_registro == '0460':
                bloco.registro_0001.registros_0460.append(
                    Registro0460.ler_registro(registro)
                )

            # Nivel 2 - Filho de 0001
            if tipo_registro == '0500':
                bloco.registro_0001.registros_0500.append(
                    Registro0500.ler_registro(registro)
                )

            # Nivel 2 - Filho de 0001
            if tipo_registro == '0600':
                bloco.registro_0001.registros_0600.append(
                    Registro0600.ler_registro(registro)
                )

            # Nivel 1 - Encerramento do Bloco 0
            if tipo_registro == '0990':
                bloco.registro_0990 = Registro0990.ler_registro(registro)

        return bloco

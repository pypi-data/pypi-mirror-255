from typing import List
from ..models import Bloco
from .registro_9001 import Registro9001
from .registro_9999 import Registro9999
from .registro_9990 import Registro9990
from .registro_9900 import Registro9900


class Bloco9(Bloco):
    def __init__(self):
        self.registro_9001: Registro9001 = None
        self.registro_9990: Registro9990 = None
        self.registro_9999: Registro9999 = None

    @classmethod
    def ler_registros(cls, registros: List[str]) -> 'Bloco9':
        bloco = cls()

        for registro in registros:
            tipo_registro = registro[1:5].upper()

            # Nivel 1 - Registro Pai
            if tipo_registro == '9001':
                bloco.registro_9001 = Registro9001.ler_registro(registro)

            # Nivel 1 - Encerramento do Bloco 9
            if tipo_registro == '9990':
                bloco.registro_9990 = Registro9990.ler_registro(registro)

            # Nivel 2 - Filho de 9001
            if tipo_registro == '9900':
                bloco.registro_9001.registros_9900.append(
                    Registro9900.ler_registro(registro)
                )

            # Nivel 0 - Encerramento do arquivo
            # Ultimo Registro do arquivo
            elif tipo_registro == '9999':
                bloco.registro_9999 = Registro9999.ler_registro(registro)

        return bloco

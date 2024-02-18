from typing import List
from ..models import Bloco


class Bloco1(Bloco):
    def __init__(self):
        pass

    @classmethod
    def ler_registros(cls, registros: List[str]) -> 'Bloco1':
        bloco = cls()

        for registro in registros:
            tipo_registro = registro[1:5].upper()

        return bloco

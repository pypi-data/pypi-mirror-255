from typing import List
from ..models import Bloco


class BlocoG(Bloco):
    def __init__(self):
        pass

    @classmethod
    def ler_registros(cls, registros: List[str]) -> 'BlocoG':
        bloco = cls()

        for registro in registros:
            tipo_registro = registro[1:5].upper()

        return bloco

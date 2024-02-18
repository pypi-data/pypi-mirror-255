from typing import List
from ..models import Bloco


class BlocoH(Bloco):
    def __init__(self):
        pass

    @classmethod
    def ler_registros(cls, registros: List[str]) -> 'BlocoH':
        bloco = cls()

        for registro in registros:
            tipo_registro = registro[1:5].upper()

        return bloco

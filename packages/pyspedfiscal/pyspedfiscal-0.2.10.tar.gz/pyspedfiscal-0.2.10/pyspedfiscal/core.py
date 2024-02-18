from .bloco_0 import Bloco0
from .bloco_b import BlocoB
from .bloco_c import BlocoC
from .bloco_d import BlocoD
from .bloco_e import BlocoE
from .bloco_g import BlocoG
from .bloco_h import BlocoH
from .bloco_k import BlocoK
from .bloco_1 import Bloco1
from .bloco_9 import Bloco9

import re
from pyspedfiscal.exception import ArquivoInvalido


class SpedFiscal:
    def __init__(self) -> None:
        self.bloco_0: Bloco0 = None
        self.bloco_b: BlocoB = None
        self.bloco_c: BlocoC = None
        self.bloco_d: BlocoD = None
        self.bloco_e: BlocoE = None
        self.bloco_g: BlocoG = None
        self.bloco_h: BlocoH = None
        self.bloco_k: BlocoK = None
        self.bloco_1: Bloco1 = None
        self.bloco_9: Bloco9 = None

    def validar(self, arquivo: str):

        bloco_0000_pattern = r'^(\|0000\|)(\d){3,}\|[0,1]\|((\d){8,}\|){2}(.{0,100})\|(\d){,14}\|(\d){,11}\|.{2,}\|.{0,14}\|(\d){0,7}\|.*\|.{0,9}\|[a,b,c,A,B,C]\|[0,1]\|$'

        try:
            with open(arquivo, 'r', encoding='latin-1') as arq_sped:
                bloco_0000 = next(arq_sped)
        except OSError as e:
            raise OSError("Não foi possível ler o arquivo:\n", repr(e))
        except Exception as e:
            raise Exception(
                "Erro inesperado, entre em contato com o suporte:\n", repr(e))
        else:
            return bool(re.match(bloco_0000_pattern, bloco_0000))

    @classmethod
    def importar(cls, arquivo: str) -> 'SpedFiscal':
        """Importa um arquivo Sped

        Args:
            arquivo (str): Arquivo Sped

        Raises:
            ArquivoInvalido: Erros de validação no arquivo
        """

        sped = cls()

        # Valida o arquivo
        if not sped.validar(arquivo):
            raise ArquivoInvalido(arquivo)

        with open(arquivo, 'r', encoding='latin-1') as arq_sped:

            resgitros = arq_sped.readlines()

            # Remove as linhas que não são registro
            resgitros = [
                registro for registro in resgitros if registro.startswith('|')
            ]

            sped.bloco_0 = Bloco0.ler_registros(resgitros)
            sped.bloco_b = BlocoB.ler_registros(resgitros)
            sped.bloco_c = BlocoC.ler_registros(resgitros)
            sped.bloco_d = BlocoD.ler_registros(resgitros)
            sped.bloco_e = BlocoE.ler_registros(resgitros)
            sped.bloco_g = BlocoG.ler_registros(resgitros)
            sped.bloco_h = BlocoH.ler_registros(resgitros)
            sped.bloco_k = BlocoK.ler_registros(resgitros)
            sped.bloco_1 = Bloco1.ler_registros(resgitros)
            sped.bloco_9 = Bloco9.ler_registros(resgitros)

        return sped

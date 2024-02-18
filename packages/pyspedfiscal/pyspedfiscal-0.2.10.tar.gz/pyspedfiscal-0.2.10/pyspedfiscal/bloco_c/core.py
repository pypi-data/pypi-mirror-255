from typing import List
from ..models import Bloco
from .registro_c001 import RegistroC001
from .registro_c100 import RegistroC100
from .registro_c101 import RegistroC101
from .registro_c105 import RegistroC105
from .registro_c110 import RegistroC110
from .registro_c111 import RegistroC111
from .registro_c112 import RegistroC112
from .registro_c113 import RegistroC113
from .registro_c114 import RegistroC114
from .registro_c115 import RegistroC115
from .registro_c116 import RegistroC116
from .registro_c120 import RegistroC120
from .registro_c130 import RegistroC130
from .registro_c140 import RegistroC140
from .registro_c141 import RegistroC141
from .registro_c160 import RegistroC160
from .registro_c165 import RegistroC165
from .registro_c170 import RegistroC170
from .registro_c180 import RegistroC180
from .registro_c190 import RegistroC190
from .registro_c195 import RegistroC195
from .registro_c197 import RegistroC197


class BlocoC(Bloco):
    def __init__(self):
        self.registro_c001: RegistroC001 = None

    @classmethod
    def ler_registros(cls, registros: List[str]) -> 'BlocoC':
        bloco = cls()

        for registro in registros:
            tipo_registro = registro[1:5].upper()

            # Nivel 1 - Registro Pai
            if tipo_registro == 'C001':
                bloco.registro_c001 = RegistroC001.ler_registro(registro)

            # Nivel 2 - Filho de C001
            elif tipo_registro == 'C100':
                bloco.registro_c001.registros_c100.append(RegistroC100.ler_registro(registro))

            # Nivel 3 - Filho de C100
            elif tipo_registro == 'C101':
                bloco.registro_c001.registros_c100[-1].registros_c101 = RegistroC101.ler_registro(
                    registro
                )

            # Nivel 3 - Filho de C100
            elif tipo_registro == 'C105':
                bloco.registro_c001.registros_c100[-1].registros_c105 = RegistroC105.ler_registro(
                    registro
                )

            # Nivel 3 - Filho de C100
            elif tipo_registro == 'C110':
                bloco.registro_c001.registros_c100[-1].registros_c110.append(
                    RegistroC110.ler_registro(registro)
                )

            # Nivel 4 - Filho de C110
            elif tipo_registro == 'C111':
                bloco.registro_c001.registros_c100[-1].registros_c110[-1].registros_c111.append(
                    RegistroC111.ler_registro(registro)
                )

            # Nivel 4 - Filho de C110
            elif tipo_registro == 'C112':
                bloco.registro_c001.registros_c100[-1].registros_c110[-1].registros_c112.append(
                    RegistroC112.ler_registro(registro)
                )

            # Nivel 4 - Filho de C110
            elif tipo_registro == 'C113':
                bloco.registro_c001.registros_c100[-1].registros_c110[-1].registros_c113.append(
                    RegistroC113.ler_registro(registro)
                )

            # Nivel 4 - Filho de C110
            elif tipo_registro == 'C114':
                bloco.registro_c001.registros_c100[-1].registros_c110[-1].registros_c114.append(
                    RegistroC114.ler_registro(registro)
                )

            # Nivel 4 - Filho de C110
            elif tipo_registro == 'C115':
                bloco.registro_c001.registros_c100[-1].registros_c110[-1].registros_c115.append(
                    RegistroC115.ler_registro(registro)
                )

            # Nivel 4 - Filho de C110
            elif tipo_registro == 'C116':
                bloco.registro_c001.registros_c100[-1].registros_c110[-1].registros_c116.append(
                    RegistroC116.ler_registro(registro)
                )

            # Nivel 3 - Filho de C100
            elif tipo_registro == 'C120':
                bloco.registro_c001.registros_c100[-1].registros_c120.append(
                    RegistroC120.ler_registro(registro)
                )

            # Nivel 3 - Filho de C100
            elif tipo_registro == 'C130':
                bloco.registro_c001.registros_c100[-1].registro_c130 = RegistroC130.ler_registro(registro)

            # Nivel 3 - Filho de C100
            elif tipo_registro == 'C140':
                bloco.registro_c001.registros_c100[-1].registro_c140 = RegistroC140.ler_registro(registro)

            # Nivel 4 - Filho de C140
            elif tipo_registro == 'C141':
                bloco.registro_c001.registros_c100[-1].registro_c140.registros_c141.append(
                    RegistroC141.ler_registro(registro)
                )

            # Nivel 3 - Filho de C100
            elif tipo_registro == 'C160':
                bloco.registro_c001.registros_c100[-1].registro_c160 = RegistroC160.ler_registro(registro)

            # Nivel 4 - Filho de C160
            elif tipo_registro == 'C165':
                bloco.registro_c001.registros_c100[-1].registro_c160.registros_c165.append(
                    RegistroC165.ler_registro(registro)
                )

            # Nivel 3 - Filho de C100
            elif tipo_registro == 'C170':
                bloco.registro_c001.registros_c100[-1].registros_c170.append(
                    RegistroC170.ler_registro(registro)
                )

            # Nivel 3 - Filho de C100
            elif tipo_registro == 'C180':
                bloco.registro_c001.registros_c100[-1].registro_c180 = RegistroC180.ler_registro(registro)

            # Nivel 3 - Filho de C100
            elif tipo_registro == 'C190':
                bloco.registro_c001.registros_c100[-1].registros_c190.append(RegistroC190.ler_registro(registro))

            # Nivel 3 - Filho de C100
            elif tipo_registro == 'C195':
                bloco.registro_c001.registros_c100[-1].registros_c195.append(RegistroC195.ler_registro(registro))

            # Nivel 4 - Filho de C195
            elif tipo_registro == 'C197':
                bloco.registro_c001.registros_c100[-1].registros_c195[-1].registros_c197.append(
                    RegistroC197.ler_registro(registro)
                )

        return bloco

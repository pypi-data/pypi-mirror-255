from pyspedfiscal import SpedFiscal
import unittest
from pathlib import Path


arquivo_teste = Path(__file__).parent / 'arquivos' / 'arquivo_teste.txt'


class TestSpedFiscal(unittest.TestCase):

    def test_deve_ler_um_arquivo_sped_fiscal(self):
        sped_fiscal = SpedFiscal.importar(arquivo_teste)
        assert sped_fiscal.bloco_0.registro_0000.cnpj == 14028298000152

    def test_deve_validar_um_arquivo_fiscal(self):

        esperado = True

        sped_fiscal = SpedFiscal()
        eh_valido = sped_fiscal.validar(arquivo_teste)

        self.assertEqual(eh_valido, esperado)


if __name__ == '__main__':
    unittest.main()

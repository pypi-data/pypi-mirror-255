from datetime import date
from pyspedfiscal.bloco_9 import Bloco9
import unittest


class TestBloco9(unittest.TestCase):

    def setUp(self) -> None:

        bloco = """
|9001|0|
|9900|0000|1|
|9900|0001|1|
|9900|0002|1|
|9900|9900|55|
|9990|58|
|9999|140|
""".splitlines()

        self.bloco_9 = Bloco9.ler_registros(bloco)

    def test_deve_ler_um_registro_9001(self):
        reg = self.bloco_9.registro_9001.reg
        ind_mov = self.bloco_9.registro_9001.ind_mov

        self.assertEqual(reg, '9001')
        self.assertEqual(ind_mov, '0')

    def test_deve_ler_um_registro_9900(self):
        registro_9900 = self.bloco_9.registro_9001.registros_9900[0]

        self.assertEqual(registro_9900.reg, '9900')
        self.assertEqual(registro_9900.reg_blc, '0000')
        self.assertEqual(registro_9900.qtd_reg_blc, 1)

    def test_deve_ler_um_registro_9990(self):
        registro_9990 = self.bloco_9.registro_9990

        self.assertEqual(registro_9990.reg, '9990')
        self.assertEqual(registro_9990.qtd_lin_9, 58)

    def test_deve_ler_um_registro_9999(self):
        reg = self.bloco_9.registro_9999.reg
        qtd_lin = self.bloco_9.registro_9999.qtd_lin

        self.assertEqual(reg, '9999')
        self.assertEqual(qtd_lin, 140)


if __name__ == '__main__':
    unittest.main()

from decimal import Decimal
from pyspedfiscal.bloco_e import BlocoE
import unittest
from datetime import date


class TestBlocoE(unittest.TestCase):

    def setUp(self) -> None:

        bloco = """
|E001|0|
|E100|01072022|31072022|
|E110|0|0|0|0|16,63|2984,9|0|0|0|0|0|0|3001,53|0|
|E115|RJ000001|100|Teste1|
|E300|RJ|01072022|31072022|
|E310|0|0|20|0|0|0|20|0|20|0|0|0|100|0|0|0|100|0|100|0|0|
|E300|SP|01072022|31072022|
|E310|0|0|80|0|0|0|80|0|80|0|0|0|0|0|0|0|0|0|0|0|0|
|E500|0|01072022|31072022|
|E520|0|0|0|0|0|0|0|
|E990|11|""".splitlines()

        self.bloco_e = BlocoE.ler_registros(bloco)

    def test_deve_ler_um_registro_e001(self):
        registro_e001 = self.bloco_e.registro_e001

        reg = registro_e001.reg
        ind_mov = registro_e001.ind_mov

        self.assertEqual(reg, 'E001')
        self.assertEqual(ind_mov, '0')

    def test_deve_ler_um_registro_e100(self):
        resgitro_e100 = self.bloco_e.registro_e001.registros_e100[0]

        reg = resgitro_e100.reg
        dt_ini = resgitro_e100.dt_ini
        dt_fin = resgitro_e100.dt_fin

        self.assertEqual(reg, 'E100')
        self.assertEqual(dt_ini, date(2022, 7, 1))
        self.assertEqual(dt_fin, date(2022, 7, 31))

    def test_deve_ler_um_registro_e110(self):
        registro_e110 = self.bloco_e.registro_e001.registros_e100[0].registros_e110[0]

        reg = registro_e110.reg
        vl_tot_creditos = registro_e110.vl_tot_creditos
        vl_aj_creditos = registro_e110.vl_aj_creditos
        vl_sld_credor_transportar = registro_e110.vl_sld_credor_transportar

        self.assertEqual(reg, 'E110')
        self.assertEqual(vl_tot_creditos, Decimal('16.63'))
        self.assertEqual(vl_aj_creditos, Decimal('2984.9'))
        self.assertEqual(vl_sld_credor_transportar, Decimal('3001.53'))

    def test_deve_ler_um_registro_e115(self):
        registro_c115 = self.bloco_e.registro_e001.registros_e100[
            0].registros_e110[0].registros_c115[0]

        reg = registro_c115.reg
        cod_inf_adic = registro_c115.cod_inf_adic
        vl_inf_adic = registro_c115.vl_inf_adic
        descr_compl_aj = registro_c115.descr_compl_aj

        self.assertEqual(reg, 'E115')
        self.assertEqual(cod_inf_adic, 'RJ000001')
        self.assertEqual(vl_inf_adic, Decimal('100'))
        self.assertEqual(descr_compl_aj, 'Teste1')


if __name__ == '__main__':
    unittest.main()

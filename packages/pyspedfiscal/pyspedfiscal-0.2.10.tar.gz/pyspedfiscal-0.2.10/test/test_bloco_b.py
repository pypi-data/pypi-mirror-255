from datetime import date
from pyspedfiscal.bloco_b import BlocoB
from pyspedfiscal.bloco_b.registro_b001 import IndDad
from pyspedfiscal.bloco_b.registro_b020 import IndEmit, IndOper
from pyspedfiscal.bloco_b.registro_b440 import IndOper as IndOperB440
from pyspedfiscal.bloco_b.registro_b460 import IndDed, IndProc
from pyspedfiscal.tabelas import CodModIss, CodSit
from pyspedfiscal.bloco_b.registro_b510 import IndProf, IndEsc, IndSoc
import unittest
from decimal import Decimal


class TestBlocoB(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:

        bloco = """
|B001|0|
|B020|0|1|1|55|00||10|33220714028298000152550010000000011000147724|01072022|1100064|110|11|10|11|11|10|10|20|11|1|
|B025|10|2|10|10|10|0104|
|B030|3A|1|1|10|01072022|1|100|10|10|10|1|
|B035|10|10|10|12|22|3501|
|B350|10|Conta Teste|71707002|10|0102|100|10|10|111|1|
|B420|200|10|10|110|10|2201|
|B440|0|2|100|11|100|
|B440|1|3|1000|20|22|
|B460|2|1525|22|2|Decricao Teste|1|0|
|B470|100|10|10|20|30|22|1|33|20|10|10|10|10|10|
|B500|100|1|100|
|B510|0|0|0|12345678909|Funcionario Teste|
|B990|13|
""".splitlines()

        cls.bloco_b = BlocoB.ler_registros(bloco)

    def test_deve_ler_um_registro_b001(self):
        registros_b001 = self.bloco_b.registro_b001

        # |B001|0|

        self.assertEqual(registros_b001.reg, 'B001')
        self.assertEqual(registros_b001.ind_dad, IndDad.com_dados_informados)

    def test_deve_ler_um_registro_b020(self):
        registro_b020 = self.bloco_b.registro_b001.registros_b020[0]

        # |B020|0|1|1|55|00||10|33220714028298000152550010000000011000147724|01072022|1100064|110|11|10|11|11|10|10|20|11|1|

        self.assertEqual(registro_b020.reg, 'B020')
        self.assertEqual(registro_b020.ind_oper, IndOper.aquisicao)
        self.assertEqual(registro_b020.ind_emit, IndEmit.terceiros)
        self.assertEqual(registro_b020.cod_part, '1')
        self.assertEqual(registro_b020.cod_mod, CodModIss.nota_fiscal_eletronica)
        self.assertEqual(registro_b020.cod_sit, CodSit.regular)
        self.assertEqual(registro_b020.ser, None)
        self.assertEqual(registro_b020.num_doc, 10)
        self.assertEqual(registro_b020.dt_doc, date(2022, 7, 1))
        self.assertEqual(registro_b020.cod_mun_serv, '1100064')
        self.assertEqual(registro_b020.vl_cont, Decimal('110'))
        self.assertEqual(registro_b020.vl_mat_terc, Decimal('11'))
        self.assertEqual(registro_b020.vl_sub, Decimal('10'))
        self.assertEqual(registro_b020.vl_isnt_iss, Decimal('11'))
        self.assertEqual(registro_b020.vl_ded_bc, Decimal('11'))
        self.assertEqual(registro_b020.vl_bc_iss, Decimal('10'))
        self.assertEqual(registro_b020.vl_bc_iss_rt, Decimal('10'))
        self.assertEqual(registro_b020.vl_iss_rt, Decimal('20'))
        self.assertEqual(registro_b020.vl_iss, Decimal('11'))
        self.assertEqual(registro_b020.cod_inf_obs, '1')

    def test_deve_ler_um_registro_b025(self):
        registro_b025 = self.bloco_b.registro_b001.registros_b020[0].registros_b250[0]

        # |B025|10|2|10|10|10|0104|

        self.assertEqual(registro_b025.reg, 'B025')
        self.assertEqual(registro_b025.vl_cont_p, Decimal('10'))
        self.assertEqual(registro_b025.vl_bc_iss_p, Decimal('2'))
        self.assertEqual(registro_b025.aliq_iss, Decimal('10'))
        self.assertEqual(registro_b025.vl_iss_p, Decimal('10'))
        self.assertEqual(registro_b025.vl_isnt_iss_p, Decimal('10'))
        self.assertEqual(registro_b025.cod_serv, '0104')

    def test_deve_ler_um_registro_b030(self):
        registro_b030 = self.bloco_b.registro_b001.registros_b030[0]

        # |B030|3A|1|1|10|01072022|1|100|10|10|10|1|

        self.assertEqual(registro_b030.reg, 'B030')
        self.assertEqual(registro_b030.cod_mod, CodModIss.nota_fiscal_servico_simp)
        self.assertEqual(registro_b030.ser, '001')
        self.assertEqual(registro_b030.num_doc_ini, 1)
        self.assertEqual(registro_b030.num_doc_fin, 10)
        self.assertEqual(registro_b030.dt_doc, date(2022, 7, 1))
        self.assertEqual(registro_b030.qtd_canc, 1)
        self.assertEqual(registro_b030.vl_cont, Decimal('100'))
        self.assertEqual(registro_b030.vl_isnt_iss, Decimal('10'))
        self.assertEqual(registro_b030.vl_bc_iss, Decimal('10'))
        self.assertEqual(registro_b030.vl_iss, Decimal('10'))
        self.assertEqual(registro_b030.cod_inf_obs, '1')

    def test_deve_ler_um_registro_b035(self):
        registro_b035 = self.bloco_b.registro_b001.registros_b030[0].registros_b035[0]

        # |B035|10|10|10|12|22|3501|

        self.assertEqual(registro_b035.reg, 'B035')
        self.assertEqual(registro_b035.vl_cont_p, Decimal('10'))
        self.assertEqual(registro_b035.vl_bc_iss_p, Decimal('10'))
        self.assertEqual(registro_b035.aliq_iss, Decimal('10'))
        self.assertEqual(registro_b035.vl_iss_p, Decimal('12'))
        self.assertEqual(registro_b035.vl_isnt_iss_p, Decimal('22'))
        self.assertEqual(registro_b035.cod_serv, '3501')

    def test_deve_ler_um_registro_b350(self):
        registro_b350 = self.bloco_b.registro_b001.registros_b350[0]

        # |B350|10|Conta Teste|71707002|10|0102|100|10|10|111|1|

        self.assertEqual(registro_b350.reg, 'B350')
        self.assertEqual(registro_b350.cod_ctd, '10')
        self.assertEqual(registro_b350.cta_iss, 'Conta Teste')
        self.assertEqual(registro_b350.cta_cosif, 71707002)
        self.assertEqual(registro_b350.qtd_ocor, 10)
        self.assertEqual(registro_b350.cod_serv, 102)
        self.assertEqual(registro_b350.vl_cont, Decimal('100'))
        self.assertEqual(registro_b350.vl_bc_iss, Decimal('10'))
        self.assertEqual(registro_b350.aliq_iss, Decimal('10'))
        self.assertEqual(registro_b350.vl_iss, Decimal('111'))
        self.assertEqual(registro_b350.cod_inf_obs, '1')

    def test_deve_ler_um_registro_b420(self):
        registro_b420 = self.bloco_b.registro_b001.registros_b420[0]

        # |B420|200|10|10|110|10|2201|

        self.assertEqual(registro_b420.reg, 'B420')
        self.assertEqual(registro_b420.vl_cont, Decimal('200'))
        self.assertEqual(registro_b420.vl_bc_iss, Decimal('10'))
        self.assertEqual(registro_b420.aliq_iss, Decimal('10'))
        self.assertEqual(registro_b420.vl_isnt_iss, Decimal('110'))
        self.assertEqual(registro_b420.vl_iss, Decimal('10'))
        self.assertEqual(registro_b420.cod_serv, '2201')

    def test_deve_ler_um_registro_b440(self):
        registro_b440 = self.bloco_b.registro_b001.registros_b440[1]

        # |B440|1|3|1000|20|22|

        self.assertEqual(registro_b440.reg, 'B440')
        self.assertEqual(registro_b440.ind_oper, IndOperB440.prestacao)
        self.assertEqual(registro_b440.cod_part, '3')
        self.assertEqual(registro_b440.vl_cont_rt, Decimal('1000'))
        self.assertEqual(registro_b440.vl_bc_iss_rt, Decimal('20'))
        self.assertEqual(registro_b440.vl_iss_rt, Decimal('22'))

    def test_deve_ler_um_registro_b460(self):
        registro_b460 = self.bloco_b.registro_b001.registros_b460[0]

        # |B460|2|1525|22|2|Decricao Teste|1|0|

        self.assertEqual(registro_b460.reg, 'B460')
        self.assertEqual(registro_b460.ind_ded, IndDed.decisao_adm_judic)
        self.assertEqual(registro_b460.vl_ded, Decimal('1525'))
        self.assertEqual(registro_b460.num_proc, '22')
        self.assertEqual(registro_b460.ind_proc, IndProc.justica_estadual)
        self.assertEqual(registro_b460.proc, 'Decricao Teste')
        self.assertEqual(registro_b460.cod_inf_obs, '1')
        self.assertEqual(registro_b460.ind_obr, '0')

    def test_deve_ler_um_registro_b470(self):
        registro_b470 = self.bloco_b.registro_b001.registro_b470

        # |B470|100|10|10|20|30|22|1|33|20|10|10|10|10|10|

        self.assertEqual(registro_b470.reg, 'B470')
        self.assertEqual(registro_b470.vl_cont, Decimal('100'))
        self.assertEqual(registro_b470.vl_mat_terc, Decimal('10'))
        self.assertEqual(registro_b470.vl_mat_prop, Decimal('10'))
        self.assertEqual(registro_b470.vl_sub, Decimal('20'))
        self.assertEqual(registro_b470.vl_isnt, Decimal('30'))
        self.assertEqual(registro_b470.vl_ded_bc, Decimal('22'))
        self.assertEqual(registro_b470.vl_bc_iss, Decimal('1'))
        self.assertEqual(registro_b470.vl_bc_iss_rt, Decimal('33'))
        self.assertEqual(registro_b470.vl_iss, Decimal('20'))
        self.assertEqual(registro_b470.vl_iss_rt, Decimal('10'))
        self.assertEqual(registro_b470.vl_ded, Decimal('10'))
        self.assertEqual(registro_b470.vl_iss_rec, Decimal('10'))
        self.assertEqual(registro_b470.vl_iss_st, Decimal('10'))
        self.assertEqual(registro_b470.vl_iss_rec_uni, Decimal('10'))

    def test_deve_ler_um_registro_b500(self):
        registro_b500 = self.bloco_b.registro_b001.registro_b500

        # |B500|100|1|100|

        self.assertEqual(registro_b500.reg, 'B500')
        self.assertEqual(registro_b500.vl_rec, Decimal('100'))
        self.assertEqual(registro_b500.qtd_prof, 1)
        self.assertEqual(registro_b500.vl_or, Decimal('100'))

    def test_deve_ler_um_registro_b510(self):
        registro_b510 = self.bloco_b.registro_b001.registro_b500.registros_b510[0]

        # |B510|0|0|0|12345678909|Funcionario Teste|

        self.assertEqual(registro_b510.reg, 'B510')
        self.assertEqual(registro_b510.ind_prof, IndProf.habilitado)
        self.assertEqual(registro_b510.ind_esc, IndEsc.superior)
        self.assertEqual(registro_b510.ind_soc, IndSoc.socio)
        self.assertEqual(registro_b510.cpf, 12345678909)
        self.assertEqual(registro_b510.nome, 'Funcionario Teste')

    def test_deve_ler_um_registro_b990(self):
        registro_b990 = self.bloco_b.registro_b990

        # |B990|13|

        self.assertEqual(registro_b990.reg, 'B990')
        self.assertEqual(registro_b990.qtd_lin_b, 13)


if __name__ == '__main__':
    unittest.main()

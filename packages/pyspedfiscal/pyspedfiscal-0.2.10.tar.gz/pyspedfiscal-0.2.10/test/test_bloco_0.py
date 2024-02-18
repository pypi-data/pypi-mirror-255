from datetime import date
from decimal import Decimal
from pyspedfiscal.bloco_0 import Bloco0
from pyspedfiscal.bloco_0.registro_0000 import IndAtiv
from pyspedfiscal.bloco_0.registro_0500 import IndCTA, CodigoNatCC
import unittest
from pyspedfiscal import tabelas


class TestBloco0(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:

        bloco = """
|0000|016|0|01072022|31072022|EMPRESA TESTE|14028298000152||RJ|42497045|3300233|||A|0|
|0001|0|
|0002|00|
|0005|EMPRESA TESTE|25821270|RUA EMPRESA TESTE|1111||BAIRRO EMPRESA TESTE|2499999999|||
|0015|RJ|14201122|
|0100|CONTADOR TESTE|25142702000|1-SP-111111/O-1||25805290|RUA CONTADOR|111|ENDERECO CONTADOR|BAIRRO CONTADOR|2499999999||emailcontador@contador.com.br|3550308|
|0150|1|FORNECEDOR 1|1058|03446003000141|||3301702||ENDERECO FORNECEDOR 1|1111||BAIRRO FORNECEDOR 1|
|0175|10072022|11|155|
|0150|2|FORNECEDOR 2|1058|97509345000107|||3550308||ENDERECO FORNECEDOR 1|2222||BAIRRO FORNECEDOR 2|
|0175|10072022|11|154|
|0150|3|FORNECEDOR 3|1058|05929208000103|||3550308||ENDERECO FORNECEDOR 1|3333||BAIRRO FORNECEDOR 3|
|0175|10072022|11|152|
|0150|4|FORNECEDOR 4|1058|13992567000133|||3550308||ENDERECO FORNECEDOR 1|4444||BAIRRO FORNECEDOR 4|
|0175|10072022|11|153|
|0150|5|FORNECEDOR 5|1058|38284654000167|||3550308||ENDERECO FORNECEDOR 1|5555||BAIRRO FORNECEDOR 5|
|0175|10072022|11|145|
|0175|11072022|03|FORNECEDOR 11|
|0190|KG|KILO|
|0190|UN|UNIDADE|
|0200|1|PRODUTO 1|||UN|00|27101921||||||
|0205|PRODUTO 1 ANTERIOR|01012022|31012022|11|
|0206|110101001|
|0210|1|10|1|
|0220|KG|15|PRODUTO|
|0200|2|PRODUTO 2|||KG|00|27101921||||||
|0200|3|PRODUTO 3|||KG|00|27101921||||||
|0200|4|PRODUTO 4|||KG|00|27101921||||||
|0200|5|PRODUTO 5|||KG|00|27101921||||||
|0300|1|1|BEM TESTE|1|1|5|
|0305|TESTE|TESTE|5|
|0400|1653002|Natureza Teste|
|0450|1|Informacao Complementar Teste|
|0460|1|Observacao Teste|
|0500|01012022|01|A|1|1|CONTA TESTE|
|0600|01012022|TESTE|TESTE|
|0990|32|""".splitlines()

        cls.bloco_0 = Bloco0.ler_registros(bloco)

    def test_deve_ler_um_registro_0000(self):
        registro_0000 = self.bloco_0.registro_0000

        # |0000|016|0|01072022|31072022|EMPRESA TESTE|14028298000152||RJ|42497045|3300233|||A|0|

        self.assertEqual(registro_0000.reg, '0000')
        self.assertEqual(registro_0000.cod_ver, '016')
        self.assertEqual(registro_0000.cod_fin, '0')
        self.assertEqual(registro_0000.dt_ini, date(2022, 7, 1))
        self.assertEqual(registro_0000.dt_fin, date(2022, 7, 31))
        self.assertEqual(registro_0000.nome, 'EMPRESA TESTE')
        self.assertEqual(registro_0000.cnpj, 14028298000152)
        self.assertEqual(registro_0000.cpf, None)
        self.assertEqual(registro_0000.uf, 'RJ')
        self.assertEqual(registro_0000.ie, '42497045')
        self.assertEqual(registro_0000.cod_mun, 3300233)
        self.assertEqual(registro_0000.im, None)
        self.assertEqual(registro_0000.suframa, None)
        self.assertEqual(registro_0000.ind_perfil, 'A')
        self.assertEqual(registro_0000.ind_ativ, IndAtiv.industrial)

    def test_deve_ler_um_registro_0001(self):
        registro_0001 = self.bloco_0.registro_0001

        reg = registro_0001.reg
        ind_mov = registro_0001.ind_mov

        # |0001|0|

        self.assertEqual(reg, '0001')
        self.assertEqual(ind_mov, '0')

    def test_deve_ler_um_registro_0002(self):
        registro_0002 = self.bloco_0.registro_0001.registro_0002

        reg = registro_0002.reg
        clas_estab_ind = registro_0002.clas_estab_ind

        # |0002|00|

        self.assertEqual(reg, '0002')
        self.assertEqual(clas_estab_ind, tabelas.ClassifContribIpi.industrial_transformacao)

    def test_deve_ler_um_registro_0005(self):
        registro_0005 = self.bloco_0.registro_0001.registro_0005

        reg = registro_0005.reg
        fantasia = registro_0005.fantasia
        cep = registro_0005.cep
        end = registro_0005.end
        num = registro_0005.num
        compl = registro_0005.compl
        bairro = registro_0005.bairro
        fone = registro_0005.fone
        fax = registro_0005.fax
        email = registro_0005.email

        # |0005|EMPRESA TESTE|25821270|RUA EMPRESA TESTE|1111||BAIRRO EMPRESA TESTE|2499999999|||

        self.assertEqual(reg, '0005')
        self.assertEqual(fantasia, 'EMPRESA TESTE')
        self.assertEqual(cep, 25821270)
        self.assertEqual(end, 'RUA EMPRESA TESTE')
        self.assertEqual(num, '1111')
        self.assertEqual(compl, None)
        self.assertEqual(bairro, 'BAIRRO EMPRESA TESTE')
        self.assertEqual(fone, '2499999999')
        self.assertEqual(fax, None)
        self.assertEqual(email, None)

    def test_deve_ler_um_registro_0015(self):
        registros_0015 = self.bloco_0.registro_0001.registros_0015[0]

        # |0015|RJ|14201122|

        self.assertEqual(registros_0015.reg, '0015')
        self.assertEqual(registros_0015.uf_st, 'RJ')
        self.assertEqual(registros_0015.ie_st, '14201122')

    def test_deve_ler_um_registro_0100(self):
        registro_0100 = self.bloco_0.registro_0001.registro_0100

        # |0100|CONTADOR TESTE|25142702000|1-SP-111111/O-1||25805290|RUA CONTADOR|111|ENDERECO CONTADOR|BAIRRO CONTADOR|2499999999||emailcontador@contador.com.br|3550308|

        self.assertEqual(registro_0100.reg, '0100')
        self.assertEqual(registro_0100.nome, 'CONTADOR TESTE')
        self.assertEqual(registro_0100.cpf, 25142702000)
        self.assertEqual(registro_0100.crc, '1-SP-111111/O-1')
        self.assertEqual(registro_0100.cnpj, None)
        self.assertEqual(registro_0100.cep, 25805290)
        self.assertEqual(registro_0100.end, 'RUA CONTADOR')
        self.assertEqual(registro_0100.num, '111')
        self.assertEqual(registro_0100.compl, 'ENDERECO CONTADOR')
        self.assertEqual(registro_0100.bairro, 'BAIRRO CONTADOR')
        self.assertEqual(registro_0100.fone, '2499999999')
        self.assertEqual(registro_0100.fax, None)
        self.assertEqual(registro_0100.email, 'emailcontador@contador.com.br')
        self.assertEqual(registro_0100.cod_mun, 3550308)

    def test_deve_ler_um_registro_0150(self):
        registro_0150 = self.bloco_0.registro_0001.registros_0150[0]

        # |0150|1|FORNECEDOR 1|1058|03446003000141|||3301702||ENDERECO FORNECEDOR 1|1111||BAIRRO FORNECEDOR 1|

        self.assertEqual(registro_0150.reg, '0150')
        self.assertEqual(registro_0150.cod_part, '1')
        self.assertEqual(registro_0150.nome, 'FORNECEDOR 1')
        self.assertEqual(registro_0150.cod_pais, 1058)
        self.assertEqual(registro_0150.cnpj, 3446003000141)
        self.assertEqual(registro_0150.cpf, None)
        self.assertEqual(registro_0150.ie, None)
        self.assertEqual(registro_0150.cod_mun, 3301702)
        self.assertEqual(registro_0150.suframa, None)
        self.assertEqual(registro_0150.end, 'ENDERECO FORNECEDOR 1')
        self.assertEqual(registro_0150.num, '1111')
        self.assertEqual(registro_0150.compl, None)
        self.assertEqual(registro_0150.bairro, 'BAIRRO FORNECEDOR 1')

    def test_deve_ler_um_registro_0175(self):
        registro_0175_1 = self.bloco_0.registro_0001.registros_0150[-1].registros_0175[0]
        registro_0175_2 = self.bloco_0.registro_0001.registros_0150[-1].registros_0175[1]

        # |0175|10072022|11|145|
        # |0175|11072022|03|FORNECEDOR 11|

        self.assertEqual(registro_0175_1.reg, '0175')
        self.assertEqual(registro_0175_1.dt_alt, date(2022, 7, 10))
        self.assertEqual(registro_0175_1.nr_campo, '11')
        self.assertEqual(registro_0175_1.cont_ant, '145')

        self.assertEqual(registro_0175_2.reg, '0175')
        self.assertEqual(registro_0175_2.dt_alt, date(2022, 7, 11))
        self.assertEqual(registro_0175_2.nr_campo, '03')
        self.assertEqual(registro_0175_2.cont_ant, 'FORNECEDOR 11')

    def test_deve_ler_um_registro_0190(self):
        registro_0190 = self.bloco_0.registro_0001.registros_0190[0]

        # |0190|KG|KILO|

        self.assertEqual(registro_0190.reg, '0190')
        self.assertEqual(registro_0190.unid, 'KG')
        self.assertEqual(registro_0190.descr, 'KILO')

    def test_deve_ler_um_registro_0200(self):
        registro_0200 = self.bloco_0.registro_0001.registros_0200[1]

        # |0200|2|PRODUTO 2|||KG|00|27101921||||||

        self.assertEqual(registro_0200.reg, '0200')
        self.assertEqual(registro_0200.cod_item, '2')
        self.assertEqual(registro_0200.descr_item, 'PRODUTO 2')
        self.assertEqual(registro_0200.cod_barra, None)
        self.assertEqual(registro_0200.cod_ant_item, None)
        self.assertEqual(registro_0200.unid_inv, 'KG')
        self.assertEqual(registro_0200.tipo_item, '00')
        self.assertEqual(registro_0200.cod_ncm, '27101921')
        self.assertEqual(registro_0200.ex_ipi, None)
        self.assertEqual(registro_0200.cod_gen, None)
        self.assertEqual(registro_0200.cod_lst, None)
        self.assertEqual(registro_0200.aliq_icms, None)
        self.assertEqual(registro_0200.cest, None)

    def test_deve_ler_um_registro_0205(self):
        registros_0205 = self.bloco_0.registro_0001.registros_0200[0].registros_0205[0]

        # |0205|PRODUTO 1 ANTERIOR|01012022|31012022|11|

        self.assertEqual(registros_0205.reg, '0205')
        self.assertEqual(registros_0205.descr_ant_item, 'PRODUTO 1 ANTERIOR')
        self.assertEqual(registros_0205.dt_ini, date(2022, 1, 1))
        self.assertEqual(registros_0205.dt_fim, date(2022, 1, 31))
        self.assertEqual(registros_0205.cod_ant_item, '11')

    def test_deve_ler_um_registro_0206(self):
        registros_0206 = self.bloco_0.registro_0001.registros_0200[0].registros_0206[0]

        # |0206|110101001|

        self.assertEqual(registros_0206.reg, '0206')
        self.assertEqual(registros_0206.cod_comb, '110101001')

    def test_deve_ler_um_registro_0210(self):
        registros_0210 = self.bloco_0.registro_0001.registros_0200[0].registros_0210[0]

        # |0210|1|10|1|

        self.assertEqual(registros_0210.reg, '0210')
        self.assertEqual(registros_0210.cod_item_comp, '1')
        self.assertEqual(registros_0210.qtd_comp, Decimal('10'))
        self.assertEqual(registros_0210.perda, Decimal('1'))

    def test_deve_ler_um_registro_0220(self):
        registros_0220 = self.bloco_0.registro_0001.registros_0200[0].registros_0220[0]

        # |0220|KG|15|PRODUTO|

        self.assertEqual(registros_0220.reg, '0220')
        self.assertEqual(registros_0220.unid_conv, 'KG')
        self.assertEqual(registros_0220.fat_conv, Decimal('15'))
        self.assertEqual(registros_0220.cod_barra, 'PRODUTO')

    def test_deve_ler_um_registro_0221(self):

        # PVA não implementou este registro
        registros_0221 = self.bloco_0.registro_0001.registros_0200[0].registros_0221

        self.assertEqual(len(registros_0221), 0)

    def test_deve_ler_um_registro_0300(self):
        registros_0300 = self.bloco_0.registro_0001.registros_0300[0]

        #   |0300|1|1|BEM TESTE|1|1|5|

        self.assertEqual(registros_0300.reg, '0300')
        self.assertEqual(registros_0300.cod_ind_bem, '1')
        self.assertEqual(registros_0300.ident_merc, '1')
        self.assertEqual(registros_0300.descr_item, 'BEM TESTE')
        self.assertEqual(registros_0300.cod_prnc, '1')
        self.assertEqual(registros_0300.cod_cta, '1')
        self.assertEqual(registros_0300.nr_parc, 5)

    def test_deve_ler_um_registro_0305(self):
        registros_0305 = self.bloco_0.registro_0001.registros_0300[0].registros_0305[0]

        #   |0305|TESTE|TESTE|5|

        self.assertEqual(registros_0305.reg, '0305')
        self.assertEqual(registros_0305.cod_ccus, 'TESTE')
        self.assertEqual(registros_0305.func, 'TESTE')
        self.assertEqual(registros_0305.vida_util, 5)

    def test_deve_ler_um_registro_0400(self):
        registros_0400 = self.bloco_0.registro_0001.registros_0400[0]

        # |0400|1653002|Natureza Teste|

        self.assertEqual(registros_0400.reg, '0400')
        self.assertEqual(registros_0400.cod_nat, '1653002')
        self.assertEqual(registros_0400.descr_nat, 'Natureza Teste')

    def test_deve_ler_um_registro_0450(self):
        registros_0450 = self.bloco_0.registro_0001.registros_0450[0]

        # |0450|1|Informacao Complementar Teste|

        self.assertEqual(registros_0450.reg, '0450')
        self.assertEqual(registros_0450.cod_inf, '1')
        self.assertEqual(registros_0450.txt, 'Informacao Complementar Teste')

    def test_deve_ler_um_registro_0460(self):
        registro_0460 = self.bloco_0.registro_0001.registros_0460[0]

        # |0460|1|Observacao Teste|

        self.assertEqual(registro_0460.reg, '0460')
        self.assertEqual(registro_0460.cod_obs, '1')
        self.assertEqual(registro_0460.txt, 'Observacao Teste')

    def test_deve_ler_um_registro_0500(self):
        registros_0500 = self.bloco_0.registro_0001.registros_0500[0]

        # |0500|01012022|01|A|1|1|CONTA TESTE|

        self.assertEqual(registros_0500.reg, '0500')
        self.assertEqual(registros_0500.dt_alt, date(2022, 1, 1))
        self.assertEqual(registros_0500.cod_nat_cc, CodigoNatCC.passivo)
        self.assertEqual(registros_0500.ind_cta, IndCTA.analitica)
        self.assertEqual(registros_0500.nivel, 1)
        self.assertEqual(registros_0500.cod_cta, '1')
        self.assertEqual(registros_0500.nome_cta, 'CONTA TESTE')

    def test_deve_ler_um_registro_0600(self):
        registros_0600 = self.bloco_0.registro_0001.registros_0600[0]

        # |0600|01012022|TESTE|TESTE|

        self.assertEqual(registros_0600.reg, '0600')
        self.assertEqual(registros_0600.dt_alt, date(2022, 1, 1))
        self.assertEqual(registros_0600.cod_ccus, 'TESTE')
        self.assertEqual(registros_0600.ccus, 'TESTE')

    def test_deve_ler_um_registro_0990(self):
        registros_0990 = self.bloco_0.registro_0990

        # |0990|32|

        self.assertEqual(registros_0990.reg, '0990')
        self.assertEqual(registros_0990.qtd_lin_0, 32)


if __name__ == '__main__':
    unittest.main()

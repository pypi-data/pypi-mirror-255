from decimal import Decimal
from datetime import date
import unittest
from pyspedfiscal.tabelas import CodMod, CodSit
from pyspedfiscal.bloco_c import BlocoC
from pyspedfiscal.bloco_c.registro_c001 import IndMov
from pyspedfiscal.bloco_c.registro_c100 import IndOper, IndPgto, IndFrt
from pyspedfiscal.bloco_c.registro_c105 import Oper
from pyspedfiscal.bloco_c.registro_c111 import IndProc
from pyspedfiscal.bloco_c.registro_c112 import CodDA
from pyspedfiscal.bloco_c.registro_c113 import IndOper
from pyspedfiscal.bloco_c.registro_c115 import IndCarga
from pyspedfiscal.bloco_c.registro_c120 import CodDocImp
from pyspedfiscal.bloco_c.registro_c140 import IndTit
from pyspedfiscal.bloco_c.registro_c170 import IndMov as IndMovItem
from pyspedfiscal.gerais import IndEmit


class TestBlocoC(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:

        bloco = """
|C001|0|
|C100|1|1|1|55|00|1|1|33220714028298000152550010000000011000147724|27072022|27072022|41961,29|2|0|0|41961,29|0|10|20|30|40|50|60|70|80|90|100|110|120|
|C101|100|20|80|
|C105|0|RJ|
|C110|1|Descricao Complementar Teste|
|C111|Processo Teste|0|
|C112|0|RJ|3|1000|100|01072022|31072022|
|C113|0|0|1|01|001||1|01072022||
|C114|02|1|1|1|01072022|
|C115|0|11111111111111|12313|12345678909|1100031|22222222222222|123||1100031|
|C116|59|1|33220714028298000152570010000002110001477205|1|01072022|
|C120|0|12|1000|11|1222|
|C130|200|10000|1212|1212|3225|36|445|
|C140|0|01|Fatura teste|10|2|11000|
|C141|1|01012022|200|
|C160|4|gfg1111|10|10|100|AM|
|C165|4|kvk1111|FF44|121|125050|35|12|12|10|Motorista|12345678909|AM|
|C170|2|1||381,563|UN|2896,06|0|0|060|5101|1653002|0|0|0|0|0|0||||0|0|0|49|2896,06|0,35|0|0|10,14|49|2896,06|0,35|0|0|10,14|4212|0|
|C171|004|10|
|C172|1000|10|100|
|C173|50|1|20122021|31032024|2|1|500|
|C174|0|155|Arma|
|C175|3|11111111111111|AC|123456abc|
|C176|01|25|5|01012022|5|10|255|122|11122222255512123132135456778787999999999888|50|1000|1|10|555|5|255|2|3|22522522522522552255665565654445556622558888|4|a01|12|10|0||5252|
|C177|110000|150|
|C178|D|2000|10|
|C180|1|10|KG|10,52|20,20|21,20|23,20|12,30|0|1000|
|C181|SP000|10|KG|1A|001|1200|11122222255512123132135456778787999999999888|01062022|1|50,01|30,99|50,20|20,30|30,40|50,20|21,30|33,20|0|0,50|
|C185|122|2|030|5106||12|UN|1500|122|588|212|3235|221|15|0|454||
|C186|10|1|010|1117||10|UN|04||10||01062022|1|12|20|30|20|11|
|C190|060|5101|0|0|0|0|0|0|0|0||
|C191|20,20|3,30|14,20|
|C195|1|FECP referente ao diferencial de al�quotas|
|C197|SP10090718|FECP referente ao diferencial de al�quotas||3256,23|0|596,98|0|
|C990|35|""".splitlines()

        cls.bloco_c = BlocoC.ler_registros(bloco)

    def test_deve_ler_um_registro_c001(self):
        registro_c001 = self.bloco_c.registro_c001

        # |C001|0|

        self.assertEqual(registro_c001.reg, 'C001')
        self.assertEqual(registro_c001.ind_mov, IndMov.com_movimento)

    def test_deve_ler_um_registro_c100(self):

        registro_c100 = self.bloco_c.registro_c001.registros_c100[0]

        # |C100|1|1|1|55|00|1|1|33220714028298000152550010000000011000147724|27072022|27072022|41961,29|2|0|0|41961,29|0|10|20|30|40|50|60|70|80|90|100|110|120|

        self.assertEqual(registro_c100.reg, 'C100')
        self.assertEqual(registro_c100.ind_oper, IndOper.saida)
        self.assertEqual(registro_c100.ind_emit, IndEmit.terceiros)
        self.assertEqual(registro_c100.cod_part, '1')
        self.assertEqual(registro_c100.cod_mod, CodMod.nota_fiscal_eletronica)
        self.assertEqual(registro_c100.cod_sit, CodSit.regular)
        self.assertEqual(registro_c100.ser, '001')
        self.assertEqual(registro_c100.num_doc, 1)
        self.assertEqual(registro_c100.chv_nfe, 33220714028298000152550010000000011000147724)
        self.assertEqual(registro_c100.dt_doc, date(2022, 7, 27))
        self.assertEqual(registro_c100.dt_e_s, date(2022, 7, 27))
        self.assertEqual(registro_c100.vl_doc, Decimal('41961.29'))
        self.assertEqual(registro_c100.ind_pgto, IndPgto.outros)
        self.assertEqual(registro_c100.vl_desc, 0)
        self.assertEqual(registro_c100.vl_abat_nt, 0)
        self.assertEqual(registro_c100.vl_merc, Decimal('41961.29'))
        self.assertEqual(registro_c100.ind_frt, IndFrt.por_conta_do_remetente)
        self.assertEqual(registro_c100.vl_frt, Decimal('10.0'))
        self.assertEqual(registro_c100.vl_seg, Decimal('20.0'))
        self.assertEqual(registro_c100.vl_out_da, Decimal('30.0'))
        self.assertEqual(registro_c100.vl_bc_icms, Decimal('40.0'))
        self.assertEqual(registro_c100.vl_icms, Decimal('50.0'))
        self.assertEqual(registro_c100.vl_bc_icms_st, Decimal('60.0'))
        self.assertEqual(registro_c100.vl_icms_st, Decimal('70.0'))
        self.assertEqual(registro_c100.vl_ipi, Decimal('80.0'))
        self.assertEqual(registro_c100.vl_pis, Decimal('90.0'))
        self.assertEqual(registro_c100.vl_cofins, Decimal('100.0'))
        self.assertEqual(registro_c100.vl_pis_st, Decimal('110.0'))
        self.assertEqual(registro_c100.vl_cofins_st, Decimal('120.0'))

    def test_deve_ler_um_registro_c101(self):

        registro_c101 = self.bloco_c.registro_c001.registros_c100[0].registros_c101

        # |C101|100|20|80|

        self.assertEqual(registro_c101.vl_fcp_uf_dest, Decimal('100'))
        self.assertEqual(registro_c101.vl_icms_uf_dest, Decimal('20'))
        self.assertEqual(registro_c101.vl_icms_uf_rem, Decimal('80'))

    def test_deve_ler_um_registro_c105(self):
        registro_c105 = self.bloco_c.registro_c001.registros_c100[0].registros_c105

        # |C105|0|RJ|

        self.assertEqual(registro_c105.reg, 'C105')
        self.assertEqual(registro_c105.oper, Oper.combustiveis_lubrificantes)
        self.assertEqual(registro_c105.uf, 'RJ')

    def test_deve_ler_um_registro_c110(self):
        registro_c110 = self.bloco_c.registro_c001.registros_c100[0].registros_c110[0]

        # |C110|1|Descricao Complementar Teste|

        self.assertEqual(registro_c110.reg, 'C110')
        self.assertEqual(registro_c110.cod_inf, '1')
        self.assertEqual(registro_c110.txt_compl, 'Descricao Complementar Teste')

    def test_deve_ler_um_registro_c111(self):

        registro_c111 = self.bloco_c.registro_c001.registros_c100[0].registros_c110[0].registros_c111[0]

        # |C111|Processo Teste|0|

        self.assertEqual(registro_c111.reg, 'C111')
        self.assertEqual(registro_c111.num_proc, 'Processo Teste')
        self.assertEqual(registro_c111.ind_proc, IndProc.sefaz)

    def test_deve_ler_um_registro_c112(self):
        registro_c112 = self.bloco_c.registro_c001.registros_c100[0].registros_c110[0].registros_c112[0]

        # |C112|0|RJ|3|1000|100|01072022|31072022|

        self.assertEqual(registro_c112.reg, 'C112')
        self.assertEqual(registro_c112.cod_da, CodDA.documento_estadual)
        self.assertEqual(registro_c112.uf, 'RJ')
        self.assertEqual(registro_c112.num_da, '3')
        self.assertEqual(registro_c112.cod_aut, '1000')
        self.assertEqual(registro_c112.vl_da, Decimal('100'))
        self.assertEqual(registro_c112.dt_vcto, date(2022, 7, 1))
        self.assertEqual(registro_c112.dt_pgto, date(2022, 7, 31))

    def test_deve_ler_um_registro_c113(self):
        registro_c113 = self.bloco_c.registro_c001.registros_c100[0].registros_c110[0].registros_c113[0]

        # |C113|0|0|1|01|001||1|01072022||

        self.assertEqual(registro_c113.reg, 'C113')
        self.assertEqual(registro_c113.ind_oper, IndOper.entrada)
        self.assertEqual(registro_c113.ind_emit, IndEmit.propria)
        self.assertEqual(registro_c113.cod_part, '1')
        self.assertEqual(registro_c113.cod_mod, CodMod.nota_fiscal)
        self.assertEqual(registro_c113.ser, '001')
        self.assertEqual(registro_c113.sub, None)
        self.assertEqual(registro_c113.num_doc, 1)
        self.assertEqual(registro_c113.dt_doc, date(2022, 7, 1))
        self.assertEqual(registro_c113.chv_doce, None)

    def test_deve_ler_um_registro_c114(self):
        registro_c114 = self.bloco_c.registro_c001.registros_c100[0].registros_c110[0].registros_c114[0]

        # |C114|02|1|1|1|01072022|

        self.assertEqual(registro_c114.reg, 'C114')
        self.assertEqual(registro_c114.cod_mod, CodMod.nota_fiscal_de_venda_consumidor)
        self.assertEqual(registro_c114.ecf_fab, '1')
        self.assertEqual(registro_c114.ecf_cx, 1)
        self.assertEqual(registro_c114.num_doc, 1)
        self.assertEqual(registro_c114.dt_doc, date(2022, 7, 1))

    def test_deve_ler_um_registro_c115(self):
        registro_c115 = self.bloco_c.registro_c001.registros_c100[0].registros_c110[0].registros_c115[0]

        # |C115|0|11111111111111|12313|12345678909|1100031|22222222222222|123||1100031|

        self.assertEqual(registro_c115.reg, 'C115')
        self.assertEqual(registro_c115.ind_carga, IndCarga.rodoviario)
        self.assertEqual(registro_c115.cnpj_col, 11111111111111)
        self.assertEqual(registro_c115.ie_col, '12313')
        self.assertEqual(registro_c115.cpf_col, 12345678909)
        self.assertEqual(registro_c115.cod_mun_col, 1100031)
        self.assertEqual(registro_c115.cnpj_entg, 22222222222222)
        self.assertEqual(registro_c115.ie_entg, '123')
        self.assertEqual(registro_c115.cpf_entg, None)
        self.assertEqual(registro_c115.cod_mun_entg, 1100031)

    def test_deve_ler_um_registro_c116(self):
        registro_c116 = self.bloco_c.registro_c001.registros_c100[0].registros_c110[0].registros_c116[0]

        # |C116|59|1|33220714028298000152570010000002110001477205|1|01072022|

        self.assertEqual(registro_c116.reg, 'C116')
        self.assertEqual(registro_c116.cod_mod, CodMod.cupom_fiscal_eletronico_sat)
        self.assertEqual(registro_c116.nr_sat, 1)
        self.assertEqual(registro_c116.chv_cfe, 33220714028298000152570010000002110001477205)
        self.assertEqual(registro_c116.num_cfe, 1)
        self.assertEqual(registro_c116.dt_doc, date(2022, 7, 1))

    def test_deve_ler_um_registro_c120(self):
        registro_c120 = self.bloco_c.registro_c001.registros_c100[0].registros_c120[0]

        # |C120|0|12|1000|11|1222|

        self.assertEqual(registro_c120.reg, 'C120')
        self.assertEqual(registro_c120.cod_doc_imp, CodDocImp.declaracao_importacao)
        self.assertEqual(registro_c120.num_doc_imp, '12')
        self.assertEqual(registro_c120.pis_imp, Decimal('1000'))
        self.assertEqual(registro_c120.cofins_imp, Decimal('11'))
        self.assertEqual(registro_c120.num_acdraw, '1222')

    def test_deve_ler_um_registro_c130(self):
        registro_c130 = self.bloco_c.registro_c001.registros_c100[0].registro_c130

        # |C130|200|10000|1212|1212|3225|36|445|

        self.assertEqual(registro_c130.reg, 'C130')
        self.assertEqual(registro_c130.vl_serv_nt, Decimal('200'))
        self.assertEqual(registro_c130.vl_bc_issqn, Decimal('10000'))
        self.assertEqual(registro_c130.vl_issqn, Decimal('1212'))
        self.assertEqual(registro_c130.vl_bc_irrf, Decimal('1212'))
        self.assertEqual(registro_c130.vl_irrf, Decimal('3225'))
        self.assertEqual(registro_c130.vl_bc_prev, Decimal('36'))
        self.assertEqual(registro_c130.vl_prev, Decimal('445'))

    def test_deve_ler_um_registro_c140(self):
        registro_c140 = self.bloco_c.registro_c001.registros_c100[0].registro_c140

        # |C140|0|01|Fatura teste|10|2|11000|

        self.assertEqual(registro_c140.reg, 'C140')
        self.assertEqual(registro_c140.ind_emit, IndEmit.propria)
        self.assertEqual(registro_c140.ind_tit, IndTit.cheque)
        self.assertEqual(registro_c140.desc_tit, 'Fatura teste')
        self.assertEqual(registro_c140.num_tit, '10')
        self.assertEqual(registro_c140.qtd_parc, 2)
        self.assertEqual(registro_c140.vl_tit, Decimal('11000'))

    def test_deve_ler_um_registro_c141(self):
        registro_c141 = self.bloco_c.registro_c001.registros_c100[0].registro_c140.registros_c141[0]

        # |C141|1|01012022|200|

        self.assertEqual(registro_c141.reg, 'C141')
        self.assertEqual(registro_c141.num_parc, 1)
        self.assertEqual(registro_c141.dt_vcto, date(2022, 1, 1))
        self.assertEqual(registro_c141.vl_parc, Decimal('200'))

    def test_deve_ler_um_registro_c160(self):
        registro_c160 = self.bloco_c.registro_c001.registros_c100[0].registro_c160

        # |C160|4|gfg1111|10|10|100|AM|

        self.assertEqual(registro_c160.reg, 'C160')
        self.assertEqual(registro_c160.cod_part, '4')
        self.assertEqual(registro_c160.veic_id, 'gfg1111')
        self.assertEqual(registro_c160.qtd_vol, 10)
        self.assertEqual(registro_c160.peso_brt, Decimal('10'))
        self.assertEqual(registro_c160.peso_liq, Decimal('100'))
        self.assertEqual(registro_c160.uf_id, 'AM')

    def test_deve_ler_um_registro_c165(self):
        registro_c165 = self.bloco_c.registro_c001.registros_c100[0].registro_c160.registros_c165[0]

        # |C165|4|kvk1111|FF44|121|125050|35|12|12|10|Motorista|12345678909|AM|

        self.assertEqual(registro_c165.reg, 'C165')
        self.assertEqual(registro_c165.cod_part, '4')
        self.assertEqual(registro_c165.veic_id, 'kvk1111')
        self.assertEqual(registro_c165.cod_aut, 'FF44')
        self.assertEqual(registro_c165.nr_passe, '121')
        self.assertEqual(registro_c165.hora, '125050')
        self.assertEqual(registro_c165.temper, Decimal('35'))
        self.assertEqual(registro_c165.qtd_vol, 12)
        self.assertEqual(registro_c165.peso_brt, Decimal('12'))
        self.assertEqual(registro_c165.peso_liq, Decimal('10'))
        self.assertEqual(registro_c165.nom_mot, 'Motorista')
        self.assertEqual(registro_c165.cpf, 12345678909)
        self.assertEqual(registro_c165.uf_id, 'AM')

    def test_deve_ler_um_registro_c170(self):
        registro_c170 = self.bloco_c.registro_c001.registros_c100[0].registros_c170[0]

        # |C170|2|1||381,563|UN|2896,06|0|0|060|5101|1653002|0|0|0|0|0|0||||0|0|0|49|2896,06|0,35|0|0|10,14|49|2896,06|0,35|0|0|10,14|4212|0|

        self.assertEqual(registro_c170.reg, 'C170')
        self.assertEqual(registro_c170.num_item, 2)
        self.assertEqual(registro_c170.cod_item, '1')
        self.assertEqual(registro_c170.descr_compl, None)
        self.assertEqual(registro_c170.qtd, Decimal('381.563'))
        self.assertEqual(registro_c170.unid, 'UN')
        self.assertEqual(registro_c170.vl_item, Decimal('2896.06'))
        self.assertEqual(registro_c170.vl_desc, Decimal('0'))
        self.assertEqual(registro_c170.ind_mov, IndMovItem.sim)
        self.assertEqual(registro_c170.cst_icms, 60)
        self.assertEqual(registro_c170.cfop, 5101)
        self.assertEqual(registro_c170.cod_nat, '1653002')
        self.assertEqual(registro_c170.vl_bc_icms, Decimal('0'))
        self.assertEqual(registro_c170.aliq_icms, Decimal('0'))
        self.assertEqual(registro_c170.vl_icms, Decimal('0'))
        self.assertEqual(registro_c170.vl_bc_icms_st, Decimal('0'))
        self.assertEqual(registro_c170.aliq_st, Decimal('0'))
        self.assertEqual(registro_c170.vl_icms_st, Decimal('0'))
        self.assertEqual(registro_c170.ind_apur, None)
        self.assertEqual(registro_c170.cst_ipi, None)
        self.assertEqual(registro_c170.cod_enq, None)
        self.assertEqual(registro_c170.vl_bc_ipi, Decimal('0'))
        self.assertEqual(registro_c170.aliq_ipi, Decimal('0'))
        self.assertEqual(registro_c170.vl_ipi, Decimal('0'))
        self.assertEqual(registro_c170.cst_pis, 49)
        self.assertEqual(registro_c170.vl_bc_pis, Decimal('2896.06'))
        self.assertEqual(registro_c170.aliq_pis_percent, Decimal('0.35'))
        self.assertEqual(registro_c170.quant_bc_pis, Decimal('0'))
        self.assertEqual(registro_c170.aliq_pis, Decimal('0'))
        self.assertEqual(registro_c170.vl_pis, Decimal('10.14'))
        self.assertEqual(registro_c170.cst_cofins, 49)
        self.assertEqual(registro_c170.vl_bc_cofins, Decimal('2896.06'))
        self.assertEqual(registro_c170.aliq_cofins_percent, Decimal('0.35'))
        self.assertEqual(registro_c170.quant_bc_cofins, Decimal('0'))
        self.assertEqual(registro_c170.aliq_cofins, Decimal('0'))
        self.assertEqual(registro_c170.vl_cofins, Decimal('10.14'))
        self.assertEqual(registro_c170.cod_cta, '4212')
        self.assertEqual(registro_c170.vl_abat_nt, Decimal('0'))

    def test_deve_ler_um_registro_c171(self):
        registro_c170 = self.bloco_c.registro_c001.registros_c100[0].registros_c170[0]


if __name__ == '__main__':
    unittest.main()

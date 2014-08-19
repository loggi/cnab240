
try:
    import unittest2 as unittest
except ImportError:
    import unittest

import os
import codecs

from cnab240 import errors
from cnab240.bancos import itau
from cnab240.tipos import Lote
from tests.data import get_itau_data_from_file, DEFAULT_HEADER


class TestLote(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestLote, self).__init__(*args, **kwargs)
        self.maxDiff = None

    def setUp(self):
        itau_data = get_itau_data_from_file()
        self.header = itau_data['header_arquivo']
        self.header_lote = itau_data['header_lote']
        self.lote = itau_data['lote_cob']
        self.evento_1 = itau_data['evento_cob1']
        self.evento_2 = itau_data['evento_cob2']
        self.remessa = itau_data['remessa']

    def test_init(self):
        self.assertEqual(self.lote.eventos, [])
        self.assertEqual(self.lote.trailer.quantidade_registros, 1)

    def test_adicionar_evento(self):
        with self.assertRaises(TypeError):
            self.lote.adicionar_evento(None)

        self.lote.adicionar_evento(self.evento_1)
        self.assertEqual(self.lote.trailer.quantidade_registros, 3)

        self.lote.adicionar_evento(self.evento_2)
        self.assertEqual(self.lote.trailer.quantidade_registros, 5)

    def test_unicode(self):

        header = itau.registros.HeaderLoteCobranca(**DEFAULT_HEADER)
        header.data_credito = self.evento_1.data_emissao_titulo
        trailer = itau.registros.TrailerLoteCobranca()

        lote = Lote(itau, header, trailer)
        lote.codigo = 1

        header.controlecob_numero = int(
            '{0}{1:02}'.format(self.header.arquivo_sequencia, lote.codigo)
        )
        header.controlecob_data_gravacao = self.header.arquivo_data_de_geracao

        with self.assertRaises(errors.NenhumEventoError):
            unicode(lote)

        lote.adicionar_evento(self.evento_1)
        lote.adicionar_evento(self.evento_2)

        _gen = unicode(lote).splitlines()
        _remessa = self.remessa.splitlines()
        for ix, l in enumerate(_gen, 1):
            assert _remessa[ix] == l, "Error on line {}\n{}\n{}".format(
                ix, l, _remessa[ix]
            )


    def test_definir_codigo(self):
        self.lote.adicionar_evento(self.evento_1)
        self.lote.codigo = 129

        self.assertEqual(self.lote.header.controle_lote, 129)
        self.assertEqual(self.lote.trailer.controle_lote, 129)
        for evento in self.lote.eventos:
            for seg in evento.segmentos:
                self.assertEqual(seg.controle_lote, 129)


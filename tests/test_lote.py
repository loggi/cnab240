
try:
    import unittest2 as unittest
except ImportError:
    import unittest

import os
import codecs

from cnab240 import errors
from cnab240.bancos import itau
from cnab240.tipos import Lote
from tests.data import get_itau_data_from_file


class TestLote(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestLote, self).__init__(*args, **kwargs)
        self.maxDiff = None

    def setUp(self):
        itau_data = get_itau_data_from_file()
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
        with self.assertRaises(errors.NenhumEventoError):
            unicode(self.lote)

        import ipdb; ipdb.set_trace()
        self.lote.adicionar_evento(self.evento_1)
        self.lote.adicionar_evento(self.evento_2)

        _gen = unicode(self.lote).splitlines()
        _remessa = self.remessa.splitlines()
        for ix, l in enumerate(_remessa[1:]):
            assert _gen[ix] == l, "Error on line {}\n{}\n{}".format(
                ix, _gen[ix], l
            )


    def test_definir_codigo(self):
        self.lote.adicionar_evento(self.evento_1)
        self.lote.codigo = 129

        self.assertEqual(self.lote.header.controle_lote, 129)
        self.assertEqual(self.lote.trailer.controle_lote, 129)
        for evento in self.lote.eventos:
            for seg in evento.segmentos:
                self.assertEqual(seg.controle_lote, 129)


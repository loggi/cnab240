
try:
    import unittest2 as unittest
except ImportError:
    import unittest

import os
import codecs
from cStringIO import StringIO

from cnab240 import errors
from cnab240.bancos import itau
from cnab240.tipos import Arquivo
from tests.data import(
    get_itau_data_from_dict, get_itau_file_remessa, ARQS_DIRPATH,
    get_nonascii_data
)


class TestCnab240(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestCnab240, self).__init__(*args, **kwargs)
        self.maxDiff = None

    def setUp(self):
        self.itau_data = get_itau_data_from_dict()
        self.arquivo = Arquivo(itau, **self.itau_data['arquivo'])

    def test_unicode(self):
        self.arquivo.incluir_cobranca(**self.itau_data['cobranca'])
        self.arquivo.incluir_cobranca(**self.itau_data['cobranca2'])

        _file = unicode(self.arquivo).splitlines()
        _itau = get_itau_file_remessa().splitlines()

        for ix, l in enumerate(_file):
            assert l == _itau[ix], "Error on line {}\n{}\n{}".format(
                ix, l, _itau[ix]
            )

    def test_to_file_is_unicode(self):
        """ We check that what we write is what we are testing.

        Just to avoid regressions or being blind with bugs.
        Also, UTF-8 sanitization happens on dumping to file,
        so we have a special test below
        """
        self.arquivo.incluir_cobranca(**self.itau_data['cobranca'])
        self.arquivo.incluir_cobranca(**self.itau_data['cobranca2'])

        strio = StringIO()
        self.arquivo.escrever(strio)

        _file = strio.getvalue().splitlines()
        _unicode = unicode(self.arquivo).splitlines()

        strio.close()

        for ix, l in enumerate(_file):
            assert l == _unicode[ix], u"Error on line {}\n{}\n{}".format(
                ix, l, _unicode[ix]
            )

    def test_nonascii(self):
        """ Test if we can handle nonascii chars. """
        nonascii = get_nonascii_data()
        self.arquivo.incluir_cobranca(**nonascii['cobranca'])
        self.arquivo.incluir_cobranca(**nonascii['cobranca2'])

        strio = StringIO()
        self.arquivo.escrever(strio)

        _file = strio.getvalue().splitlines()
        _itau = get_itau_file_remessa().splitlines()

        strio.close()


        for ix, l in enumerate(_file):
            assert l == _itau[ix], u"Error on line {}\n{}\n{}".format(
                ix, l, _itau[ix]
            )

    def test_empty_data(self):
        arquivo = Arquivo(itau)
        self.assertRaises(errors.ArquivoVazioError, unicode, arquivo)

    def test_leitura(self):
        return_file_path = os.path.join(ARQS_DIRPATH, 'cobranca.itau.ret')
        with codecs.open(return_file_path, encoding='ascii') as ret_file:
            arquivo = Arquivo(itau, arquivo=ret_file)
            ret_file.seek(0)
            self.assertEqual(ret_file.read(), unicode(arquivo))

if __name__ == '__main__':
    unittest.main()

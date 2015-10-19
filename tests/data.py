# encoding: utf-8
""" All fixture data for tests.

Everything is conveniently contained with wrapper methods..
Ok, not so convenient, but still, it's ok..
"""

import os
import codecs
from decimal import Decimal
from cnab240.bancos import itau
from cnab240.tipos import Lote, Evento

TESTS_DIRPATH = os.path.abspath(os.path.dirname(__file__))
ARQS_DIRPATH = os.path.join(TESTS_DIRPATH, 'arquivos')
DEFAULT_HEADER = {
    'cedente_inscricao_tipo': 2,
    'cedente_inscricao_numero': 15594050000111,
    'cedente_agencia': 4459,
    'cedente_conta': 17600,
    'cedente_agencia_conta_dv': 6,
    'cedente_nome': u"TRACY TECNOLOGIA LTDA ME",
    'arquivo_data_de_geracao': 27062012,
    'arquivo_hora_de_geracao': 112000,
    'arquivo_sequencia': 900002
}

def get_itau_data_from_file():
    itau_data = dict()
    arquivo_remessa = codecs.open(
        os.path.join(ARQS_DIRPATH, 'cnab.rem'), encoding='ascii'
    )

    itau_data['remessa'] = arquivo_remessa.read()
    arquivo_remessa.seek(0)

    itau_data['header_arquivo_cobranca'] = itau.registros.HeaderArquivoCobranca()
    itau_data['header_arquivo_cobranca_str'] = arquivo_remessa.readline().strip('\r\n')
    itau_data['header_arquivo_cobranca'].carregar(itau_data['header_arquivo_cobranca_str'])

    itau_data['header_lote'] = itau.registros.HeaderLoteCobranca()
    itau_data['header_lote_str'] = arquivo_remessa.readline().strip('\r\n')
    itau_data['header_lote'].carregar(itau_data['header_lote_str'])

    itau_data['seg_p1'] = itau.registros.SegmentoP()
    itau_data['seg_p1_str'] = arquivo_remessa.readline().strip('\r\n')
    itau_data['seg_p1'].carregar(itau_data['seg_p1_str'])

    itau_data['seg_q1'] = itau.registros.SegmentoQ()
    itau_data['seg_q1_str'] = arquivo_remessa.readline().strip('\r\n')
    itau_data['seg_q1'].carregar(itau_data['seg_q1_str'])

    itau_data['seg_p2'] = itau.registros.SegmentoP()
    itau_data['seg_p2_str'] = arquivo_remessa.readline().strip('\r\n')
    itau_data['seg_p2'].carregar(itau_data['seg_p2_str'])

    itau_data['seg_q2'] = itau.registros.SegmentoQ()
    itau_data['seg_q2_str'] = arquivo_remessa.readline().strip('\r\n')
    itau_data['seg_q2'].carregar(itau_data['seg_q2_str'])

    itau_data['trailer_lote'] = itau.registros.TrailerLoteCobranca()
    itau_data['trailer_lote_str'] = arquivo_remessa.readline().strip('\r\n')
    itau_data['trailer_lote'].carregar(itau_data['trailer_lote_str'])

    itau_data['trailer_arquivo'] = itau.registros.TrailerArquivo()
    itau_data['trailer_arquivo_str'] = arquivo_remessa.readline().strip('\r\n')
    itau_data['trailer_arquivo'].carregar(itau_data['trailer_arquivo_str'])

    itau_data['lote_cob'] = Lote(itau, itau_data['header_lote'],
                                 itau_data['trailer_lote'])

    itau_data['evento_cob1'] = Evento(itau, 1)
    itau_data['evento_cob1'].adicionar_segmento(itau_data['seg_p1'])
    itau_data['evento_cob1'].adicionar_segmento(itau_data['seg_q1'])

    itau_data['evento_cob2'] = Evento(itau, 1)
    itau_data['evento_cob2'].adicionar_segmento(itau_data['seg_p2'])
    itau_data['evento_cob2'].adicionar_segmento(itau_data['seg_q2'])

    arquivo_remessa.close()
    return itau_data

def get_itau_data_from_dict():
    itau_data = dict()

    dict_cobranca = {
        'cedente_agencia': 4459,
        'cedente_conta': 17600,
        'cedente_agencia_conta_dv': 6,
        'carteira_numero': 109,
        'nosso_numero': 90000000,
        'nosso_numero_dv': 2,
        'numero_documento': u'9999999998',
        'vencimento_titulo': 30062012,
        'valor_titulo': Decimal('100.00'),
        'especie_titulo': 8,
        'aceite_titulo': u'A',
        'data_emissao_titulo': 27062012,
        'data_credito': 27062012,
        'juros_mora_taxa_dia': Decimal('2.00'),
        'valor_abatimento': Decimal('0.00'),
        'identificacao_titulo': u'',
        'codigo_protesto': 3,
        'prazo_protesto': 0,
        'codigo_baixa': 0,
        'prazo_baixa': 0,
        'sacado_inscricao_tipo': 1,
        'sacado_inscricao_numero': 36644661874,
        'sacado_nome': u'DAVI OLIVEIRA CAMPOS',
        'sacado_endereco': u'RUA ARLINDO CATELLI 735 AP 12',
        'sacado_bairro': u'JD PALMARES',
        'sacado_cep': 14092,
        'sacado_cep_sufixo': 530,
        'sacado_cidade': u'RIBEIRAO PRETO',
        'sacado_uf': u'SP',
        'sacador_inscricao_tipo': 2,
        'sacador_inscricao_numero': 15594050000111,
        'sacador_nome': u'TRACY TECNOLOGIA LTDA ME',
    }

    dict_cobranca2 = {
        'cedente_agencia': 4459,
        'cedente_conta': 17600,
        'cedente_agencia_conta_dv': 6,
        'carteira_numero': 109,
        'nosso_numero': 1,
        'nosso_numero_dv': 9,
        'numero_documento': u'9999999999',
        'vencimento_titulo': 1072012,
        'valor_titulo': Decimal('200.00'),
        'especie_titulo': 8,
        'aceite_titulo': u'A',
        'data_emissao_titulo': 27062012,
        'data_credito': 27062012,
        'juros_mora_taxa_dia': Decimal('2.00'),
        'valor_abatimento': Decimal('0.00'),
        'identificacao_titulo': u'',
        'codigo_protesto': 3,
        'prazo_protesto': 0,
        'codigo_baixa': 0,
        'prazo_baixa': 0,
        'sacado_inscricao_tipo': 1,
        'sacado_inscricao_numero': 33155515880,
        'sacado_nome': u'SERGIO OLIVEIRA CAMPOS',
        'sacado_endereco': u'RUA MAESTRO JOAQUIM THOME LEITE 713',
        'sacado_bairro': u'CASTELO BRANCO',
        'sacado_cep': 14090,
        'sacado_cep_sufixo': 610,
        'sacado_cidade': u'RIBEIRAO PRETO',
        'sacado_uf': u'SP',
        'sacador_inscricao_tipo': 2,
        'sacador_inscricao_numero': 15594050000111,
        'sacador_nome': u'TRACY TECNOLOGIA LTDA ME',
    }

    itau_data['arquivo'] = DEFAULT_HEADER
    itau_data['cobranca'] = dict_cobranca
    itau_data['cobranca2'] = dict_cobranca2

    return itau_data

def get_nonascii_data():
    """ We fixture for non-ascii tests.

    We take the previous dict and replace the strings with
    non-ascii chars (such as accents) and expect the return to be the same.
    """
    mod = get_itau_data_from_dict()
    mod['cobranca']['sacado_cidade'] = u'RIBEIRÃO PRETO'
    # Sorry, but I had to test with ç
    mod['cobranca']['sacado_endereco'] = u'RUA ARLINDO ÇATELLI 735 AP 12'

    mod['cobranca2']['sacado_cidade'] = u'RIBEIRÃO PRETO'
    mod['cobranca2']['sacado_nome'] = u'SÉRGIO OLIVEIRA CAMPOS'
    mod['cobranca2']['sacado_endereco'] = u'RUA MAESTRO JOAQUIM THOMÉ LEITE 713'

    return mod

def get_itau_file_remessa():
    arquivo_remessa = codecs.open(
        os.path.join(ARQS_DIRPATH, 'cnab.rem'), encoding='ascii')
    arquivo_data = arquivo_remessa.read()
    arquivo_remessa.close()
    return arquivo_data

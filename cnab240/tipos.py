# encoding: utf8
""" Cnab 240 classes.

Everything related to reading/writing Cnab 240.
"""

import codecs
import unicodedata

from datetime import datetime
from cnab240 import errors


class Evento(object):

    """ Every event that might generate one or more records.

    All the work related to events (such as a bank slip) goes here.
    """

    def __init__(self, banco, controle_registro=1):
        self.segmentos = []
        self.banco = banco
        # constante, 1
        self.controle_registro = 1
        self._codigo_lote = None

    def adicionar_segmento(self, segmento):
        """ Add the event type to the segment.

        Assure that every segment added to the event holds the same
        event type.
        """
        # Codigo da ocorrência, Nota 4: remessa == 1
        segmento.servico_codigo_movimento = 1
        self.segmentos.append(segmento)

    def __getattribute__(self, name):
        """ Make `segmentos` transparently available. """
        for segmento in object.__getattribute__(self, 'segmentos'):
            if hasattr(segmento, name):
                return getattr(segmento, name)
        return object.__getattribute__(self, name)

    def __unicode__(self):
        return u'\r\n'.join(unicode(seg) for seg in self.segmentos)

    def __len__(self):
        return len(self.segmentos)

    @property
    def codigo_lote(self):
        return self._codigo_lote

    @codigo_lote.setter
    def codigo_lote(self, valor):
        self._codigo_lote = valor
        for segmento in self.segmentos:
            segmento.controle_lote = valor

    def atualizar_codigo_registros(self, last_id):
        current_id = last_id
        for segmento in self.segmentos:
            current_id += 1
            segmento.servico_numero_registro = current_id
        return current_id


class Lote(object):

    def __init__(self, banco, header=None, trailer=None):
        self.banco = banco
        self.header = header
        self.trailer = trailer
        self._codigo = None
        self.trailer.quantidade_registros = 2
        self._eventos = []

    @property
    def codigo(self):
        return self._codigo

    @codigo.setter
    def codigo(self, valor):
        self._codigo = valor
        self.header.controle_lote = valor
        self.trailer.controle_lote = valor
        self.atualizar_codigo_eventos()

    def atualizar_codigo_eventos(self):
        for evento in self._eventos:
            evento.codigo_lote = self._codigo

    def atualizar_codigo_registros(self):
        last_id = 0
        for evento in self._eventos:
             last_id = evento.atualizar_codigo_registros(last_id)

    @property
    def eventos(self):
        return self._eventos

    def adicionar_evento(self, evento):
        if not isinstance(evento, Evento):
            raise TypeError

        self._eventos.append(evento)
        self.trailer.cobrancasimples_quantidade_titulos += len(evento)
        self.atualizar_codigo_registros()

        if self._codigo:
            self.atualizar_codigo_eventos()

    def __unicode__(self):
        if not self._eventos:
            raise errors.NenhumEventoError()

        result = []
        result.append(unicode(self.header))
        result.extend(unicode(evento) for evento in self._eventos)
        result.append(unicode(self.trailer))
        return '\r\n'.join(result)

    def __len__(self):
        return self.trailer.quantidade_registros


class Arquivo(object):

    def __init__(self, banco, **kwargs):
        """Arquivo Cnab240."""

        self._lotes = []
        self.banco = banco
        arquivo = kwargs.get('arquivo')
        if isinstance(arquivo, (file, codecs.StreamReaderWriter)):
            return self.carregar_retorno(arquivo)

        self.header = self.banco.registros.HeaderArquivo(**kwargs)
        self.trailer = self.banco.registros.TrailerArquivo(**kwargs)
        self.trailer.totais_quantidade_lotes = 0
        self.trailer.totais_quantidade_registros = 2

        if self.header.arquivo_data_de_geracao is None:
            now = datetime.now()
            self.header.arquivo_data_de_geracao = int(now.strftime("%d%m%Y"))

        if self.header.arquivo_hora_de_geracao is None:
            if now is None:
                now = datetime.now()
            self.header.arquivo_hora_de_geracao = int(now.strftime("%H%M%S"))

    def carregar_retorno(self, arquivo):

        lote_aberto = None
        evento_aberto = None

        for linha in arquivo:
            tipo_registro = linha[7]

            if tipo_registro == '0':
                self.header = self.banco.registros.HeaderArquivo()
                self.header.carregar(linha)

            elif tipo_registro == '1':
                codigo_servico = linha[9:11]

                if codigo_servico == '01':
                    header_lote = self.banco.registros.HeaderLoteCobranca()
                    header_lote.carregar(linha)
                    trailer_lote = self.banco.registros.TrailerLoteCobranca()
                    lote_aberto = Lote(self.banco, header_lote, trailer_lote)
                    self._lotes.append(lote_aberto)

            elif tipo_registro == '3':
                tipo_segmento = linha[13]
                codigo_evento = linha[15:17]

                if tipo_segmento == 'T':
                    seg_t = self.banco.registros.SegmentoT()
                    seg_t.carregar(linha)

                    evento_aberto = Evento(self.banco)
                    lote_aberto._eventos.append(evento_aberto)
                    evento_aberto.segmentos.append(seg_t)

                elif tipo_segmento == 'U':
                    seg_u = self.banco.registros.SegmentoU()
                    seg_u.carregar(linha)
                    evento_aberto.segmentos.append(seg_u)
                    evento_aberto = None

            elif tipo_registro == '5':
                if trailer_lote is not None:
                    lote_aberto.trailer.carregar(linha)
                else:
                    raise Exception

            elif tipo_registro == '9':
                self.trailer = self.banco.registros.TrailerArquivo()
                self.trailer.carregar(linha)

    @property
    def lotes(self):
        return self._lotes

    def incluir_cobranca(self, **kwargs):
        evento = Evento(self.banco)

        seg_p = self.banco.registros.SegmentoP(**kwargs)
        evento.adicionar_segmento(seg_p)

        seg_q = self.banco.registros.SegmentoQ(**kwargs)
        evento.adicionar_segmento(seg_q)

        header = self.banco.registros.HeaderLoteCobranca(**self.header.todict())
        trailer = self.banco.registros.TrailerLoteCobranca()
        lote_cobranca = Lote(self.banco, header, trailer)
        self.adicionar_lote(lote_cobranca)

        if header.controlecob_numero is None:
            header.controlecob_numero = int('{0}{1:02}'.format(
                self.header.arquivo_sequencia,
                lote_cobranca.codigo))

        if header.controlecob_data_gravacao is None:
            header.controlecob_data_gravacao = self.header.arquivo_data_de_geracao

        lote_cobranca.adicionar_evento(evento)
        # Incrementar numero de registros no trailer do arquivo
        self.trailer.totais_quantidade_registros += len(evento)

    def encontrar_lote(self, codigo_servico):
        for lote in self.lotes:
            if lote.header.servico_servico == codigo_servico:
                return lote

    def adicionar_lote(self, lote):
        if not isinstance(lote, Lote):
            raise TypeError('Objeto deve ser instancia de "Lote"')

        self._lotes.append(lote)
        lote.codigo = len(self._lotes)

        # Incrementar numero de lotes no trailer do arquivo
        self.trailer.totais_quantidade_lotes += 1

    def escrever(self, file_):
        value = unicode(self)

        sanitized = unicodedata.normalize(
            'NFKD', value
        ).encode('ascii', 'ignore').decode('ascii')

        file_.write(sanitized.encode('ascii'))

    def dump(self):
        """ Dump itself into a new file. """
        filename = "{}{}.rem".format(
            unicode(self.header.arquivo_data_de_geracao)[:4],
            unicode(self.header.arquivo_sequencia)
        )

        with file(filename, 'w') as dump:
            self.escrever(dump)


    def __unicode__(self):
        if not self._lotes:
            raise errors.ArquivoVazioError()

        result = []
        result.append(unicode(self.header))
        result.extend(unicode(lote) for lote in self._lotes)
        result.append(unicode(self.trailer))
        # Adicionar elemento vazio para arquivo terminar com \r\n
        result.append(u'')
        return u'\r\n'.join(result)


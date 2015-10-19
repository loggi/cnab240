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

    def __init__(self, banco, codigo_evento=1):
        self.segmentos = []
        self.banco = banco
        self.codigo_evento = codigo_evento
        self._codigo_lote = None

    def adicionar_segmento(self, segmento):
        """ Add the event type to the 'Segmento'.

        Assure that every 'Segmento' added to the event holds the same
        event type.
        """
        segmento.servico_codigo_movimento = self.codigo_evento
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
        # We take the header in here...
        self.trailer.quantidade_registros = 1
        self.last_id = 0
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
        _add = self.atualizar_codigo_evento
        [_add(evento) for evento in self._eventos]

    def atualizar_codigo_evento(self, evento):
        evento.codigo_lote = self._codigo

    def atualizar_codigo_registro(self, evento):
        self.last_id = evento.atualizar_codigo_registros(self.last_id)

    @property
    def eventos(self):
        return self._eventos

    def adicionar_evento(self, evento):
        if not isinstance(evento, Evento):
            raise TypeError

        self._eventos.append(evento)
        self.trailer.quantidade_registros += len(evento)
        self.trailer.cobrancasimples_quantidade_titulos += 1
        self.atualizar_codigo_registro(evento)

        if self._codigo:
            self.atualizar_codigo_evento(evento)

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
        self._lote_q = {}
        self.banco = banco
        arquivo = kwargs.get('arquivo')
        if isinstance(arquivo, (file, codecs.StreamReaderWriter)):
            return self.carregar_retorno_cobranca(arquivo)

        self.header = self.banco.registros.HeaderArquivoCobranca(**kwargs)
        self.trailer = self.banco.registros.TrailerArquivo(**kwargs)
        self.trailer.totais_quantidade_lotes = 0
        # Header + trailers
        self.trailer.totais_quantidade_registros = 3

        if self.header.arquivo_data_de_geracao is None:
            now = datetime.now()
            self.header.arquivo_data_de_geracao = int(now.strftime("%d%m%Y"))

        if self.header.arquivo_hora_de_geracao is None:
            if now is None:
                now = datetime.now()
            self.header.arquivo_hora_de_geracao = int(now.strftime("%H%M%S"))

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

    def __len__(self):
        """ Return the len for the current set of records. """
        return self.trailer.totais_quantidade_registros

    def carregar_retorno_cobranca(self, arquivo):

        lote_aberto = None
        evento_aberto = None

        for ix, linha in enumerate(arquivo, 1):
            tipo_registro = linha[7]

            if tipo_registro == '0':
                self.header = self.banco.registros.HeaderArquivoCobranca()
                field = self.header

            elif tipo_registro == '1':
                codigo_servico = linha[9:11]

                if codigo_servico == '01':
                    header_lote = self.banco.registros.HeaderLoteCobranca()
                    field = header_lote
                    trailer_lote = self.banco.registros.TrailerLoteCobranca()
                    lote_aberto = Lote(self.banco, header_lote, trailer_lote)
                    self._lotes.append(lote_aberto)

            elif tipo_registro == '3':
                tipo_segmento = linha[13]

                if tipo_segmento == 'T':
                    seg_t = self.banco.registros.SegmentoT()
                    field = seg_t

                    evento_aberto = Evento(self.banco)
                    lote_aberto._eventos.append(evento_aberto)
                    evento_aberto.segmentos.append(seg_t)

                elif tipo_segmento == 'U':
                    seg_u = self.banco.registros.SegmentoU()
                    field = seg_u
                    evento_aberto.segmentos.append(seg_u)
                    evento_aberto = None

            elif tipo_registro == '5':
                if trailer_lote is not None:
                    field = lote_aberto.trailer
                else:
                    raise Exception

            elif tipo_registro == '9':
                self.trailer = self.banco.registros.TrailerArquivo()
                field = self.trailer

            if field:
                field.carregar(linha, ix)

    @property
    def lotes(self):
        return self._lotes

    def size_lotes(self):
        """ Return the size of all nested 'lote's. """
        return sum([len(lote) for lote in self._lotes])

    def incluir_cobranca(self, **kwargs):
        codigo_evento = kwargs.get('servico_codigo_movimento', 1)
        evento = Evento(self.banco, codigo_evento)

        seg_p = self.banco.registros.SegmentoP(**kwargs)
        evento.adicionar_segmento(seg_p)

        seg_q = self.banco.registros.SegmentoQ(**kwargs)
        evento.adicionar_segmento(seg_q)

        return self.adicionar_evento(evento, **kwargs)

    def adicionar_evento(self, evento, **kwargs):
        lote = self._lote_q.get(evento.codigo_evento)

        if not lote:
            header = self.banco.registros.HeaderLoteCobranca(
                **self.header.todict()
            )
            header.fromdict(kwargs)
            header.servico_servico = evento.codigo_evento

            trailer = self.banco.registros.TrailerLoteCobranca()
            lote = Lote(self.banco, header, trailer)

            lote.adicionar_evento(evento)
            self._lotes.append(lote)
            self._lote_q[evento.codigo_evento] = lote
            lote.codigo = len(self._lotes)

            if not header.controlecob_numero:
                header.controlecob_numero = int('{0}{1:02}'.format(
                    self.header.arquivo_sequencia,
                    lote.codigo))

            if not header.controlecob_data_gravacao:
                header.controlecob_data_gravacao = \
                    self.header.arquivo_data_de_geracao
            self.trailer.totais_quantidade_lotes += 1
            self.trailer.totais_quantidade_registros += 1
        else:
            lote.adicionar_evento(evento)

        size_evento = len(evento)

        if len(self) + size_evento > 178:
            raise errors.ArquivoCheioError()

        self.trailer.totais_quantidade_registros += size_evento

        # Return seg_p row
        return lote.last_id - 1

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



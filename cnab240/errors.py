# -*- coding: utf-8 -*-

class Cnab240Error(Exception):
    """Excessao base para o CNAB 240"""
    pass


class AtribuicaoCampoError(Cnab240Error):
    """Tentativa de atribuicao de valor indevido ao campo"""

    def __init__(self, campo, valor=None, linha=None):
        self.campo = campo
        self.valor = valor
        self.linha = linha
        super(AtribuicaoCampoError, self).__init__(self)

    def __unicode__(self):
        return '{}: {}{}{}'.format(
            self.__class__.__name__,
            self.campo, (
                '-> {}'.format(self.valor)
                if self.valor
                else ''
            ),
            (
                ' na linha {}'.format(self.linha)
                if self.linha
                else ''
            )
        )


class NumDigitosExcedidoError(AtribuicaoCampoError):
    """Tentativa de atribuicao de valor mais longo que o campo suportaia"""
    pass


class TipoError(AtribuicaoCampoError):
    """Tentativa de atribuicao de tipo nao suportado pelo campo"""
    pass


class NumDecimaisError(AtribuicaoCampoError):
    """Numero de casasa decimais em desacordo com especificacao"""
    pass


class FaltandoArgsError(Cnab240Error):
    """Faltando argumentos na chamada do metodo"""

    def __init__(self, args_faltantes):
        self.args_faltantes = args_faltantes
        super(FaltandoArgsError, self).__init__(self)

    def __unicode__(self):
        return (u'Os seguintes kwargs sao obrigatorios e nao foram '
                u'encontrados: {0}').format(', '.join(self.args_faltantes))


class ArquivoVazioError(Cnab240Error):
    """Tentativa de escrita de arquivo vazio."""
    pass


class ArquivoCheioError(Cnab240Error):

    """ The file cannot have more than 178 rows. """

    pass


class NenhumEventoError(Cnab240Error):
    """Tentativa de escrita de lote sem eventos. """
    pass


class CampoObrigatorioError(Cnab240Error):
    """Campo obrigatorio nao preenchido."""
    pass



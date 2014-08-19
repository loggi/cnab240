# encoding: utf-8
""" All exceptions for system. """


class Cnab240Error(Exception):

    u""" Excessão base para o CNAB 240. """

    pass


class AtribuicaoCampoError(Cnab240Error):

    u""" Tentativa de atribuição de valor indevido ao campo. """

    def __init__(self, campo, valor=None, linha=None):  # noqa
        self.campo = campo
        self.valor = valor
        self.linha = linha
        super(AtribuicaoCampoError, self).__init__(self)

    def __unicode__(self):  # noqa
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

    u""" Tentativa de atribuição de valor mais longo que o campo suporta. """

    pass


class TipoError(AtribuicaoCampoError):

    u""" Tentativa de atribuição de tipo não suportado pelo campo. """

    pass


class NumDecimaisError(AtribuicaoCampoError):

    u""" Número de casasa decimais em desacordo com especificação. """

    pass


class FaltandoArgsError(Cnab240Error):

    u""" Faltando argumentos na chamada do método. """

    def __init__(self, args_faltantes):  # noqa
        self.args_faltantes = args_faltantes
        super(FaltandoArgsError, self).__init__(self)

    def __unicode__(self):  # noqa
        return (u'Os seguintes kwargs sao obrigatorios e nao foram '
                u'encontrados: {0}').format(', '.join(self.args_faltantes))


class ArquivoVazioError(Cnab240Error):

    """ Tentativa de escrita de arquivo vazio. """

    pass


class ArquivoCheioError(Cnab240Error):

    """ The file cannot have more than 178 rows. """

    pass


class NenhumEventoError(Cnab240Error):

    """Tentativa de escrita de lote sem eventos. """

    pass


class CampoObrigatorioError(Cnab240Error):

    u"""Campo obrigatório não preenchido. """

    pass

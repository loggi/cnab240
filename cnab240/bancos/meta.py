# encoding: utf-8
"""Meta info about `bancos` package.

    Centralizes access to intrinsic info of this package structure.
"""
from glob import iglob
import os
import importlib

from cnab240.registro import Registros

def get_bancos():
    cwd = os.path.abspath(os.path.dirname(__file__))
    return (fname for fname in os.listdir(cwd)
                  if os.path.isdir(os.path.join(cwd, fname)))

def get_banco_modules():
    return [importlib.import_module('.'.join((__package__, nome_banco)))
            for nome_banco in get_bancos()]

def get_spec_dir(module):
    module_path = os.path.abspath(os.path.dirname(module.__file__))
    return os.path.join(module_path, 'specs')

def get_spec_files(module):
    # TODO: Validar spec: nome (deve ser unico para cada registro),
    #   posicao_inicio, posicao_fim, formato (alpha), decimais (0),
    #   default (zeros se numerico ou brancos se alfa)
    module_path = os.path.abspath(os.path.dirname(module.__file__))
    specs_dir = os.path.join(module_path, 'specs')
    return iglob(os.path.join(specs_dir, '*.json'))


def load_registros():
    for banco_module in get_banco_modules():
        banco_module.registros = Registros(get_spec_files(banco_module))

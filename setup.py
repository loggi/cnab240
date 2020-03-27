# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
from cnab240 import __version__

setup(
    name='loggicnab240',
    version=__version__,
    author='Loggi Tecnologia LTDA',
    author_email='dev@loggi.com',
    url='https://github.com/loggi/cnab240',
    packages=find_packages(),
    package_data={
        'cnab240': ['bancos/*/*/*.json']
    },
    zip_safe=False,
    install_requires=[],
    provides=[
        'loggicnab240'
    ],
    license='LGPL',
    description='Classe para gerar arquivo de remessa e leitura de retorno no '
                                                            'padrão CNAB240',
    long_description=open('README.md', 'r').read(),
    download_url='https://github.com/loggi/cnab240',
    scripts=[],
    classifiers=[],
    platforms='any',
    test_suite='',
    tests_require=[],
)

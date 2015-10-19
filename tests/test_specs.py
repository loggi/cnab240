# encoding: utf-8
""" Specification tests. """

try:
    import unittest2 as unittest
except ImportError:
    import unittest

import cnab240.bancos

class TestSpecsHardRulesConformity(unittest.TestCase):
    """Verify specification hard rules adherence and conformity."""

    def test_240_line_length(self):
        for b in self.get_bancos():
            pass

    def get_bancos(self):
        return [banco for banco in dir(cnab240.bancos)
                if not banco.startswith("__")]
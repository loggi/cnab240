# encoding: utf-8
""" Specification tests. """
import inspect

try:
    import unittest2 as unittest
except ImportError:
    import unittest

import cnab240.bancos as banco

class TestSpecsHardRulesConformity(unittest.TestCase):
    """Verify specification hard rules adherence and conformity."""

    def test_240_line_length(self):
        for b in self.get_bancos():
            for layout in self.layouts(b.registros):
                self.assertEqual(self.sum_length(layout),
                    240, u'{} should have 240 length'.format(layout))
                self.assertEqual(self.sum_length_digitos(layout),
                                 240, u'{} should have 240 length'.format(layout))

    def test_no_overlap_neither_holes_between_data(self):
        for b in self.get_bancos():
            for layout in self.layouts(b.registros):
                # `inicio` is adjusted subtracting 1.
                # see `registo#criar_classe_campo`
                curr_end = 0
                for t in self.sorted_ini_end_tuples(layout):
                    self.assertEqual(curr_end, t[0])
                    curr_end = t[1]


    def layouts(self, registros):
        # TODO seiti - check better way to do that
        return [getattr(registros, r) for r in dir(registros)
                   if not r.startswith("__")
                   and inspect.isclass(getattr(registros, r))]

    def sum_length(self, target):
        return sum([v.fim - v.inicio for k, v in  target._campos_cls.iteritems()])

    def sum_length_digitos(self, target):
        return sum([v.digitos for k, v in  target._campos_cls.iteritems()])

    def sorted_ini_end_tuples(self, target):
        tuples = [(v.inicio, v.fim) for k, v in target._campos_cls.iteritems()]
        return sorted(tuples, key=lambda t: t[0])

    def get_bancos(self):
        return [banco.hsbc, banco.itau]


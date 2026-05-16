"""
Test parse utils'
"""

from django.test import TestCase

from src.utils.parse import to_camel_case


class TestParse(TestCase):
    def test_to_camel_case(self):
        self.assertEqual(to_camel_case("teste_de_string"), "testeDeString")
        self.assertEqual(to_camel_case("teste"), "teste")
        self.assertEqual(to_camel_case("teste_de_string_longa"), "testeDeStringLonga")

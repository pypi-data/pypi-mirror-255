# -*- coding: utf8 -*-
import unittest

from src.odoo_env_config import entry, mappers, section


class TestOdooConfig(unittest.TestCase):
    def test_all_mappers_are_register(self):
        number_of_mapper = 5
        self.assertEqual(len(mappers.__all__), number_of_mapper)
        self.assertEqual(len(entry.MAPPER), number_of_mapper)
        self.assertSetEqual(set(mappers.__all__), {mapper.__name__ for mapper in entry.MAPPER})

    def test_all_section_are_register(self):
        number_of_section = 11
        self.assertEqual(len(section.__all__), number_of_section)
        self.assertEqual(len(entry.CONVERTER), number_of_section)
        self.assertSetEqual(set(section.__all__), {mapper.__name__ for mapper in entry.CONVERTER})

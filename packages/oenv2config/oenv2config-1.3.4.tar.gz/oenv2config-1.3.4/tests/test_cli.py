# -*- coding: utf8 -*-
import unittest
from typing import List, Type

from src.odoo_env_config import api, cli
from src.odoo_env_config.cli import _load_profiles


class TestCli(unittest.TestCase):
    def test_cli1(self):
        parser = cli.get_odoo_cmd_parser()
        ns = parser.parse_args(["--profile=/tmp/profile1.env", "--profile=/tmp/profile2.env", "--dest=/tmp/dest.ini"])
        self.assertEqual(ns.config_dest, "/tmp/dest.ini")
        self.assertIn("/tmp/profile1.env", ns.profiles)
        self.assertIn("/tmp/profile2.env", ns.profiles)

    def test_cli_profiles(self):
        parser = cli.get_odoo_cmd_parser()
        ns = parser.parse_args(["--profiles=/tmp/profile1.env,/tmp/profile2.env"])
        self.assertIn("/tmp/profile1.env", ns.profiles)
        self.assertIn("/tmp/profile2.env", ns.profiles)

    def test_cli_profiles_ending_comma(self):
        parser = cli.get_odoo_cmd_parser()
        ns = parser.parse_args(["--profiles=/tmp/profile1.env,/tmp/profile2.env,"])
        self.assertIn("/tmp/profile1.env", ns.profiles)
        self.assertIn("/tmp/profile2.env", ns.profiles)
        self.assertEqual(len(ns.profiles), 2)

    def test_cli_profiles_many_comma(self):
        parser = cli.get_odoo_cmd_parser()
        ns = parser.parse_args(["--profiles=/tmp/profile1.env,,/tmp/profile2.env"])
        self.assertIn("/tmp/profile1.env", ns.profiles)
        self.assertIn("/tmp/profile2.env", ns.profiles)
        self.assertEqual(len(ns.profiles), 2)

    def test_cli_profiles_no_comma(self):
        parser = cli.get_odoo_cmd_parser()
        ns = parser.parse_args(["--profiles=/tmp/profile1.env,"])
        self.assertIn("/tmp/profile1.env", ns.profiles)
        self.assertEqual(len(ns.profiles), 1)

    def test_cli_profiles_prefix_comma(self):
        parser = cli.get_odoo_cmd_parser()
        ns = parser.parse_args(["--profiles=,/tmp/profile1.env,/tmp/profile2.env"])
        self.assertIn("/tmp/profile1.env", ns.profiles)
        self.assertIn("/tmp/profile2.env", ns.profiles)
        self.assertEqual(len(ns.profiles), 2)

    def test_cli_profiles_both_options(self):
        parser = cli.get_odoo_cmd_parser()
        ns = parser.parse_args(["--profile=/tmp/profile3.env", "--profiles=/tmp/profile1.env,/tmp/profile2.env"])
        self.assertIn("/tmp/profile1.env", ns.profiles)
        self.assertIn("/tmp/profile2.env", ns.profiles)
        self.assertIn("/tmp/profile3.env", ns.profiles)
        self.assertEqual(len(ns.profiles), 3)

    def test_cli_profiles_empty(self):
        parser = cli.get_odoo_cmd_parser()
        ns = parser.parse_args(["--profiles="])
        self.assertEqual(len(ns.profiles), 0)

    def test_load_profiles_without_profile(self):
        extra_env = _load_profiles([])
        self.assertEqual(extra_env, api.Env())


class _FakeOdooConfig:
    def __init__(self):
        self.args_parse_config: List[List[str]] = []
        self.save_is_called_nb: int = 0

    def _parse_config(self, args: List[str]):
        print(args)
        self.args_parse_config.append(args)

    def save(self):
        print("Save")
        self.save_is_called_nb += 1


class FakeOdoo:  # noqa
    def __init__(self):
        self.tools = FakeOdoo._Tools()

    class cli:  # noqa
        class Command:
            sub_command: Type = None

            def __init_subclass__(cls, **kwargs):
                FakeOdoo.cli.Command.sub_command = cls

    class _Tools:  # noqa
        def __init__(self):
            self.config = _FakeOdooConfig()


class TestOdooCommand(unittest.TestCase):
    def test_create(self):
        """
        Assert the class [cli.OdooCommand][cli.OdooCommand] is correct to make a new odoo command

        1. The name is env2config`
        2. Have 1 function names 'run'
        3. Is subclass of odoo.cli.Command in the test case `_FakeOdooCommand`

        """
        fake_odoo = FakeOdoo()
        self.assertFalse(fake_odoo.cli.Command.sub_command)
        command = cli.OdooCommand(fake_odoo)
        self.assertEqual("env2config", cli.OdooCommand.command_name())

        self.assertTrue(fake_odoo.cli.Command.sub_command)
        clazz = fake_odoo.cli.Command.sub_command

        # Assert Class is created has expected
        self.assertIn(fake_odoo.cli.Command, clazz.mro())
        self.assertEqual(cli.OdooCommand.command_name(), clazz.__name__)

        # Assert Instance have attribute has expected
        inst_clazz = clazz()
        self.assertTrue(hasattr(inst_clazz, "run"))
        self.assertEqual(getattr(inst_clazz, "run"), command.run_command)

    def test_runcommand1(self):
        """
        Assert the `run` function of the dynamic odoo.cli.Command call
        1. the save function of the config
        2. split the env parse in 2 step (env args then odoo args)
        """
        fake_odoo = FakeOdoo()
        command = cli.OdooCommand(fake_odoo)
        parser_args = ["--profile=/tmp/profile1.env", "--profile=/tmp/profile2.env", "--dest=/tmp/dest.ini"]
        odoo_args = ["-d", "my_database"]
        command.run_command(parser_args + odoo_args)
        odoo_args_res = fake_odoo.tools.config.args_parse_config
        self.assertEqual(fake_odoo.tools.config.save_is_called_nb, 1)
        self.assertEqual(len(odoo_args_res), 2)
        self.assertFalse(odoo_args_res[0], "Assert False because the file in `--profile` don't exist")
        self.assertEqual(odoo_args_res[1], odoo_args, "Assert extra odoo args are keeped")

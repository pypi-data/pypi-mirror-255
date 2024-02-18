"""
Python file containing all the function used by the cli.
`odoo_env_confi` expose a script command when installed.
>>> odoo-env2config -h

This command allow to run this libraray inside an odoo command (See `odoo.cli.Command`
"""
import argparse
import logging
import os
import subprocess
import sys
from os.path import join as pjoin
from typing import List

from dotenv import dotenv_values

from . import api, entry


def init_logger():
    _logger_level = getattr(logging, os.environ.get("NDP_SERVER_LOG_LEVEL", "INFO"), logging.INFO)
    _logger = logging.getLogger(__name__)
    _logger.setLevel(logging.DEBUG)
    _logger.addHandler(logging.StreamHandler())


class SplitArgs(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        # start or ending comma removed to avoid empty value in list
        setattr(namespace, self.dest, getattr(namespace, self.dest, []) + list(filter(None, values.split(","))))


def get_odoo_cmd_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    p.add_argument("--profile", action="append", dest="profiles", default=[], help="profile to use")
    p.add_argument(
        "--profiles", action=SplitArgs, dest="profiles", default=[], help="profiles to use (comma separated)"
    )
    p.add_argument("--dest", dest="config_dest", help="Path to odoo configuration file")
    return p


class OdooCommand:
    """
    This contains a new OdooCommand named `env2config`
    This class prupose is to use it inside an Odoo modules
    This command use `odoo_env_config` to convert the [os.environ][os.environ] to a valid Odoo config
    Args:
        --profiles List[str]: A list of env file to load as extra instead of only looking in [os.environ][os.environ]
        --dest str: The path where we store the result odoo config file.
    Examples:
        >>> python \
/odoo/bin --addons-path=odoo_env_config/odoo_modules env2config \
--profile=/tmp/profile1.env \
--profile=/tmp/profiles2.env \
--dest=/tmp
    """

    def __init__(self, odoo_module):
        self.odoo_module = odoo_module
        type(type(self).command_name(), (self.odoo_module.cli.Command,), {"run": self.run_command})

    @classmethod
    def command_name(cls) -> str:
        return "env2config"

    def run_command(self, args: List[str]):
        """
        Entrypoint of the command

        1. First we parse `args`
        2. Then we load `--profiles` if some are provided
        3. And finaly we execute [odoo_env_config][odoo_env_config.entry.env_to_odoo_args] and save it to the dest file

        Args:
            args: the args provided by Odoo
        """
        ns, sub_args = get_odoo_cmd_parser().parse_known_args(args)
        try:
            self.odoo_module.netsvc.init_logger()
        except Exception:
            pass
        # Removing blank sub_args
        # Is called with "$ENV_VAR" but ENV_VAR isn't set, then `sub_args` contains `['']
        # So we remove empty string from it

        sub_args = [s for s in sub_args if s.split()]
        odoo_config = self.odoo_module.tools.config
        odoo_config.config_file = ns.config_dest
        extra_env = _load_profiles(ns.profiles)
        env_args = entry.env_to_odoo_args(extra_env)
        odoo_config._parse_config(env_args)
        odoo_config._parse_config(sub_args)
        admin_passwd = entry.env_to_section(entry.MiscSection, extra_env).admin_password
        if admin_passwd:
            odoo_config.set_admin_password(admin_passwd)
        odoo_config.save()


def _load_profiles(profiles: List[str]) -> api.Env:
    extra_env = api.Env()
    for profile in profiles:
        path_profile = os.path.abspath(os.path.expanduser(profile))
        if not os.path.exists(path_profile):
            print("Can't load", path_profile, "file don't exist")
        else:
            extra_env.update(dotenv_values(path_profile))
    return extra_env


load_profiles = _load_profiles


def env_to_config():
    # add_help=False otherwise conflict with -h parameter of parent parser
    parser = argparse.ArgumentParser(parents=[get_odoo_cmd_parser()], add_help=False)
    parser.add_argument(
        "odoo_bin",
        default=api.Env().odoo_bin,
        nargs="?",
        help="Path to odoo-bin file, env:ODOO_BIN or /odoo/odoo-bin is used",
    )
    ns, other = parser.parse_known_args()
    parser.exit(execute_odoo_cli_helper(ns.odoo_bin, ns.profiles, ns.config_dest, other))


def execute_odoo_cli_helper(odoo_bin: str, profiles: List[str], odoo_rc: str, extra_odoo_args: List[str] = None) -> int:
    return execute_odoo_cli(
        os.path.abspath(os.path.expanduser(odoo_bin)),
        ["--profile=" + profile for profile in profiles] + ["--dest=" + odoo_rc] + extra_odoo_args,
    )


def execute_odoo_cli(odoo_bin, other) -> int:
    if not os.path.exists(odoo_bin):
        print("odoo-bin path don't exist", file=sys.stderr)
        return 1
    cmd_args = [sys.executable, odoo_bin]
    addons_path = pjoin(os.path.dirname(__file__), "odoo_modules")
    cmd_args.append(f"--addons-path={addons_path}")
    cmd_args.append(OdooCommand.command_name())  # The name of the class in odoo_modules/env2config/cli/env2config
    cmd_args.extend(other)
    print(" ".join(cmd_args))
    p = subprocess.Popen(cmd_args)
    return p.wait()

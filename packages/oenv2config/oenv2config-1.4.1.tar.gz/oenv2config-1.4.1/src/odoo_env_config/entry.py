"""

"""
import os
from typing import Callable, Dict, List, Set, Type, TypeVar

from . import api, mappers
from .section import (
    AddonsPathConfigSection,
    DatabaseOdooConfigSection,
    HttpOdooConfigSection,
    LimitOdooConfigSection,
    LoggerSection,
    MiscSection,
    S3Section,
    ServerWideModuleConfigSection,
    TestOdooConfigSection,
    UpdateInstallSection,
    WorkersOdooConfigSection,
)

Section = TypeVar("Section", bound=api.EnvConfigSection)

CONVERTER: Set[Type[Section]] = {
    AddonsPathConfigSection,
    DatabaseOdooConfigSection,
    HttpOdooConfigSection,
    LimitOdooConfigSection,
    LoggerSection,
    MiscSection,
    TestOdooConfigSection,
    UpdateInstallSection,
    ServerWideModuleConfigSection,
    WorkersOdooConfigSection,
    S3Section,
}
MAPPER: Set[Callable[[api.Env], api.Env]] = {
    mappers.compatibility,
    mappers.clevercloud_postgresql,
    mappers.redis_session,
    mappers.clevercloud_cellar,
    mappers.queue_job,
}


def apply_mapper(env: api.Env) -> api.Env:
    """
    Apply the MAPPER on `env` and return a new `api.Env` without mutate `env`
    Args:
        env: The env to map

    Returns:
        A new `api.Env` with all MAPPER applied on.
    """
    curr_env = env.copy()
    for mapper in MAPPER:
        curr_env = mapper(curr_env)
    return curr_env


def apply_converter(env: api.Env) -> api.OdooCliFlag:
    """
    Apply the CONVERTER to extract the value of `env` and return all the Odoo args founded
    Args:
        env: The env to convert to OdooCliFlag

    Returns:
        All the args found by the CONVERTER
    """
    store_values = api.OdooCliFlag()
    for converter in CONVERTER:
        store_values.update(converter().init(env).to_values())
    return store_values


def env_to_section(section: Type[Section] = None, extra_env: Dict[str, str] = None) -> Section:
    """
    Convert [environnement variables][os.environ] to a
    [Section][odoo_env_config.api.EnvConfigSection], with odoo compatible args,
    by applying a mapper and converter
    Args:
        section: A class inherited from api.EnvConfigSection, declared in CONVERTER
        extra_env: A dict to update environnement variables

    Returns:
        [A Section][odoo_env_config.api.EnvConfigSection] or False if section Class is not found in CONVERTER

    """
    if not section or section not in CONVERTER:
        return False
    curr_env = api.Env(os.environ)
    curr_env.update(extra_env or {})
    curr_env = apply_mapper(env=curr_env)
    return section().init(curr_env)


def env_to_dict(extra_env: Dict[str, str] = None) -> Dict[str, str]:
    """
    Convert [environnement variables][os.environ] to a dict, with odoo compatible args, by applying a mapper and
     converter.
    Args:
        extra_env: A dict to update environnement variables
    Returns:
        A dict with converted environnement variables
    """
    curr_env = api.Env(os.environ)
    curr_env.update(extra_env or {})
    curr_env = apply_mapper(env=curr_env)
    store_values = apply_converter(curr_env)
    return store_values


def env_to_odoo_args(extra_env: Dict[str, str] = None) -> List[str]:
    """
    Entrypoint of this library
    Convert [environnement variable][os.environ] to a odoo args valid.
    See Also
         The env to args [converter][odoo_env_config.api.EnvConfigSection]
         The speccific cloud [env mapper][odoo_env_config.mappers]
    Examples
         >>> import odoo
         >>> odoo.tools.config.parse_args(env_to_odoo_args())
         >>> odoo.tools.config.save()
    Returns:
         A list with args created from Env
    """
    curr_env = api.Env(os.environ)
    curr_env.update(extra_env or {})
    curr_env = apply_mapper(env=curr_env)
    store_values = apply_converter(curr_env)
    return api.dict_to_odoo_args(store_values)

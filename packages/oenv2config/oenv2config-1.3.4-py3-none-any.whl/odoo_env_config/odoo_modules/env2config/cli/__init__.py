"""
Odoo Commande
"""
import logging

try:
    import odoo

    from odoo_env_config import cli

    cli.OdooCommand(odoo)
except ImportError:
    logging.error("Can't import Odoo, are you sure you use this module the right way ????")

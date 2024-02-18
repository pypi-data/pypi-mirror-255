"""
Contains the mapper specifique for the environment variable provided by CleverCloud addons.
Currently we support :
- S3 addons Cellar
- Postgres Addons of any scaler
"""
from . import utils
from .api import Env

__all__ = [
    "clevercloud_cellar",
    "clevercloud_postgresql",
    "compatibility",
    "queue_job",
    "redis_session",
]


def clevercloud_cellar(curr_env: Env) -> Env:
    """ """
    return curr_env.copy().mutate(
        {
            "S3_FILESTORE_HOST": curr_env.gets(
                "S3_FILESTORE_HOST", "CELLAR_ADDON_HOST", "ODOO_S3_HOST", "MINIO_DOMAIN"
            ),
            "S3_FILESTORE_SECRET_KEY": curr_env.gets(
                "S3_FILESTORE_SECRET_KEY", "CELLAR_ADDON_KEY_SECRET", "ODOO_S3_SECRET_KEY", "MINIO_SECRET_KEY"
            ),
            "S3_FILESTORE_ACCESS_KEY": curr_env.gets(
                "S3_FILESTORE_ACCESS_KEY", "CELLAR_ADDON_KEY_ID", "ODOO_S3_ACCESS_KEY", "MINIO_ACCESS_KEY"
            ),
            "S3_FILESTORE_BUCKET": curr_env.gets("S3_FILESTORE_BUCKET", "ODOO_S3_BUCKET"),
            # Pas de region fournit par S3 CleverCloud
            "S3_FILESTORE_REGION": curr_env.gets("S3_FILESTORE_REGION", "CELLAR_ADDON_REGION", "ODOO_S3_REGION"),
            "S3_SECURE": curr_env.gets("S3_FILESTORE_SECURE", "ODOO_S3_SECURE"),
        },
    )


def clevercloud_postgresql(curr_env: Env) -> Env:
    """ """
    return curr_env.copy().mutate(
        {
            "DB_NAME": utils.get_value(curr_env, "DB_NAME", "DATABASE", "POSTGRESQL_ADDON_DB", "POSTGRES_DB"),
            "DB_HOST": utils.get_value(curr_env, "DB_HOST", "POSTGRESQL_ADDON_DIRECT_HOST", "POSTGRESQL_ADDON_HOST"),
            "DB_PORT": utils.get_value(curr_env, "DB_PORT", "POSTGRESQL_ADDON_DIRECT_PORT", "POSTGRESQL_ADDON_PORT"),
            "DB_USER": utils.get_value(curr_env, "DB_USER", "POSTGRESQL_ADDON_USER", "POSTGRES_USER"),
            "DB_PASSWORD": utils.get_value(curr_env, "DB_PASSWORD", "POSTGRESQL_ADDON_PASSWORD", "POSTGRES_PASSWORD"),
        }
    )


def compatibility(curr_env: Env) -> Env:
    """ """
    return curr_env.copy().mutate(
        {
            "WORKER_HTTP": utils.get_value(curr_env, "WORKER_HTTP", "WORKERS"),
            "WORKER_CRON": utils.get_value(curr_env, "WORKER_CRON", "CRON_THREAD", "MAX_CRON_THREAD"),
            "WORKER_JOB": utils.get_value(curr_env, "WORKER_JOB"),
            "HTTP_INTERFACE": utils.get_value(curr_env, "HTTP_INTERFACE", "XMLRPC_INTERFACE"),
            "HTTP_PORT": utils.get_value(curr_env, "HTTP_PORT", "XMLRPC_PORT"),
            "HTTP_ENABLE": utils.get_value(curr_env, "HTTP_ENABLE", "XMLRPC_ENABLE"),
            "LONGPOLLING_PORT": utils.get_value(curr_env, "LONGPOLLING_PORT"),
            "SERVER_WIDE_MODULES": utils.get_value(curr_env, "SERVER_WIDE_MODULES", "LOAD"),
        }
    )


def queue_job(curr_env: Env) -> Env:
    """ """
    new_env = curr_env.copy()
    enable = utils.to_bool(curr_env.get("ODOO_QUEUE_JOB_ENABLE"))
    if not enable:
        return new_env.mutate(ODOO_QUEUE_JOB_ENABLE=str(False))

    def copy(s):
        return [p + s for p in ["ODOO_QUEUE_JOB_", "ODOO_CONNECTOR_"]]

    return new_env.mutate(
        ODOO_QUEUE_JOB_ENABLE=str(True),
        **{
            "ODOO_QUEUE_JOB_CHANNELS": utils.get_value(curr_env, *copy("CHANNELS")),
            "ODOO_QUEUE_JOB_SCHEME": utils.get_value(curr_env, *copy("SCHEME")),
            "ODOO_QUEUE_JOB_HOST": utils.get_value(curr_env, *copy("HOST")),
            "ODOO_QUEUE_JOB_PORT": utils.get_value(curr_env, *copy("PORT")),
            "ODOO_QUEUE_JOB_HTTP_AUTH_USER": utils.get_value(curr_env, *copy("HTTP_AUTH_USER")),
            "ODOO_QUEUE_JOB_HTTP_AUTH_PASSWORD": utils.get_value(curr_env, *copy("HTTP_AUTH_PASSWORD")),
            "ODOO_QUEUE_JOB_JOBRUNNER_DB_HOST": utils.get_value(curr_env, *copy("JOBRUNNER_DB_HOST")),
            "ODOO_QUEUE_JOB_JOBRUNNER_DB_PORT": utils.get_value(curr_env, *copy("JOBRUNNER_DB_PORT")),
        },
    )


def redis_session(curr_env: Env) -> Env:
    """ """
    new_env = curr_env.copy()
    enable = curr_env.get_bool("REDIS_SESSION_ENABLE", default=bool(new_env.gets("REDIS_SESSION_HOST", "REDIS_HOST")))
    if not enable:
        return new_env.mutate(REDIS_SESSION_ENABLE=str(False))
    return new_env.mutate(
        REDIS_SESSION_ENABLE=str(True),
        **{
            "REDIS_SESSION_URL": utils.get_value(curr_env, "REDIS_SESSION_URL", "REDIS_URL"),
            "REDIS_SESSION_HOST": utils.get_value(curr_env, "REDIS_SESSION_HOST", "REDIS_HOST"),
            "REDIS_SESSION_PORT": utils.get_value(curr_env, "REDIS_SESSION_PORT", "REDIS_PORT"),
            "REDIS_SESSION_DB_INDEX": utils.get_value(curr_env, "REDIS_SESSION_DB_INDEX", "REDIS_DB_INDEX"),
            "REDIS_SESSION_PASSWORD": utils.get_value(curr_env, "REDIS_SESSION_PASSWORD", "REDIS_PASSWORD"),
        },
    )

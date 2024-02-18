import unittest

from src.odoo_env_config.api import Env
from src.odoo_env_config.section import S3Section


class TestLogSection(unittest.TestCase):
    def test_default(self):
        conf = S3Section()
        self.assertFalse(conf.access_key)
        self.assertFalse(conf.secret)
        self.assertFalse(conf.region)
        self.assertFalse(conf.host)
        self.assertFalse(conf.bucket_name)
        self.assertFalse(conf.secure)

    def test_values(self):
        conf = S3Section().init(
            Env(
                {
                    "S3_FILESTORE_ACCESS_KEY": "s3_access_value",
                    "S3_FILESTORE_SECRET_KEY": "s3_secret_value",
                    "S3_FILESTORE_BUCKET": "s3_bucket_value",
                    "S3_FILESTORE_HOST": "s3_host_value",
                    "S3_FILESTORE_REGION": "s3_region_value",
                    "S3_SECURE": "True",
                }
            )
        )
        self.assertEqual("s3_access_value", conf.access_key)
        self.assertEqual("s3_secret_value", conf.secret)
        self.assertEqual("s3_bucket_value", conf.bucket_name)
        self.assertEqual("s3_host_value", conf.host)
        self.assertEqual("s3_region_value", conf.region)
        self.assertTrue(conf.secure)

        flags = conf.to_values()
        self.assertFalse(flags)

    def test_subdir(self):
        conf = S3Section().init(
            Env(
                {
                    "S3_FILESTORE_ACCESS_KEY": "s3_access_value",
                    "S3_FILESTORE_SECRET_KEY": "s3_secret_value",
                    "S3_FILESTORE_BUCKET": "s3_bucket_value",
                    "S3_FILESTORE_HOST": "s3_host_value",
                    "S3_FILESTORE_SUB_DIR": "S3_db_name",
                    "S3_SECURE": "False",
                }
            )
        )
        self.assertEqual("s3_access_value", conf.access_key)
        self.assertEqual("s3_secret_value", conf.secret)
        self.assertEqual("s3_bucket_value", conf.bucket_name)
        self.assertEqual("s3_host_value", conf.host)
        self.assertFalse(conf.region)
        self.assertFalse(conf.secure)
        self.assertEqual("S3_db_name", conf.sub_dir)

        flags = conf.to_values()
        self.assertFalse(flags)

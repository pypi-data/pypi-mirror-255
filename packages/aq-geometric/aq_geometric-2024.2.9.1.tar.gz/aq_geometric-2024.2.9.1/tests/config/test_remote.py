import os
import unittest
from unittest.mock import patch
from sqlalchemy.engine import Engine
from aq_geometric.config.remote import get_engine


class TestRemoteConfig(unittest.TestCase):
    @patch.dict(
        os.environ, {
            "PGUSER": "test_user",
            "PGPASSWORD": "test_password",
            "PGHOST": "test_host",
            "PGDATABASE": "test_db",
            "PGPORT": "5432"
        })
    def test_get_engine(self):
        engine = get_engine()
        self.assertIsInstance(engine, Engine)
        self.assertEqual(engine.url.username, "test_user")
        self.assertEqual(engine.url.password, "test_password")
        self.assertEqual(engine.url.host, "test_host")
        self.assertEqual(engine.url.database, "test_db")
        self.assertEqual(engine.url.port, 5432)
        self.assertEqual(engine.dialect.name, "postgresql+psycopg2")
        self.assertFalse(engine.echo)
        self.assertEqual(engine.execution_options["isolation_level"],
                         "AUTOCOMMIT")
        self.assertEqual(engine.connect_args["sslmode"], "require")
        self.assertEqual(engine.pool.size, 10)
        self.assertEqual(engine.pool._max_overflow, 10)
        self.assertEqual(engine.pool._timeout, 30)


if __name__ == "__main__":
    unittest.main()

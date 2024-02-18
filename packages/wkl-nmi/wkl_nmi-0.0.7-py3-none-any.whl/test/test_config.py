import unittest
from unittest.mock import patch
from wknmi.config import Config


class TestConfig(unittest.TestCase):
    def test_get(self):
        configObj = Config(url="http://127.0.0.1:8000", org="testOrg4")
        result = configObj.get()
        self.assertEqual(result["org"], "testOrg4")

    def test_update(self):
        configObj = Config(url="http://127.0.0.1:8000", org="testOrg4")
        result = configObj.update(
            {
                "store_id": 2342311,
                "environment_active": "sandbox",
                "org": "testOrg4",
                "production_env": {"token": "4QaH5w77U2k843fu68EuB34c4M5KJ7r3"},
                "sandbox_env": {"token": "4QaH5w77U2k843fu68EuB34c4M5KJ7r3"},
                "secret_token": "4QaH5w77U2k843fu68EuB34c4M5KJ7r3",
                "merchant_orchestrator_url": "http://",
                "merchant_id": "123",
                "merchant_signature": "123",
            }
        )
        self.assertEqual(result["modified"], "1")

    def test_add(self):
        configObj = Config(url="http://127.0.0.1:8000", org="testOrg4")
        result = configObj.add(
            {
                "store_id": 234232211,
                "environment_active": "sandbox",
                "org": "testOrg5",
                "production_env": {"token": "4QaH5w77U2k843fu68EuB34c4M5KJ7r3"},
                "sandbox_env": {"token": "4QaH5w77U2k843fu68EuB34c4M5KJ7r3"},
                "secret_token": "4QaH5w77U2k843fu68EuB34c4M5KJ7r3",
                "merchant_orchestrator_url": "http://",
                "merchant_id": "123",
                "merchant_signature": "123",
            }
        )
        self.assertIsNotNone(result["inserted"])

    def test_delete(self):
        configObj = Config(url="http://127.0.0.1:8000", org="testOrg4")
        result = configObj.delete("testOrg5")
        print(result)
        self.assertEqual(result["deleted"], "1")

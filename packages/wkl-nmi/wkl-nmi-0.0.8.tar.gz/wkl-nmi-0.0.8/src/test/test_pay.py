import unittest
from unittest.mock import patch
from wknmi.payment import Pay


class TestPayments(unittest.TestCase):
    @unittest.skip("isolating testing")
    def test_with_token(self):
        pay = Pay(url="http://127.0.0.1:8000", org="testOrg")
        result = pay.with_token(
            {
                "token": "00000000-000000-000000-000000000000",
                "total": "11",
                "billingInfo": {},
            }
        )
        print(result)
        self.assertEqual(result["status_code"], 200)
        self.assertEqual(result["response"]["nm_response"]["response_code"], "100")

    @unittest.skip("isolating testing")
    def test_with_customer_vault(self):
        pay = Pay(url="http://127.0.0.1:8000", org="testOrg")
        result = pay.with_customer_vault(
            {
                "customerVault": "982f128f-8e77-4ed9-a495-1b708f79b8e2",
                "total": "2",
                "billingInfo": {},
            }
        )
        self.assertEqual(result["status_code"], 200)
        self.assertEqual(result["response"]["nm_response"]["response_code"], "100")

    def test_refund(self):
        pay = Pay(url="http://127.0.0.1:8000", org="testOrg")
        result = pay.refund("9192863564")
        print(result)
        self.assertEqual(result["status_code"], 200)
        self.assertEqual(result["response"]["nm_response"]["response_code"], "100")

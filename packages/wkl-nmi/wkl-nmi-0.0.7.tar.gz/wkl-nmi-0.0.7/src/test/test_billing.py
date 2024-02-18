import unittest
from unittest.mock import patch
from wknmi.billing import Billing


class TestBilling(unittest.TestCase):
    def test_add(self):
        billing = Billing(url="http://127.0.0.1:8000", org="testOrg4")
        result = billing.add(
            {
                "user_id": "1",
                "billing_id": "16",
                "org": "testOrg4",
                "token": "00000000-000000-000000-000000000000",
                "billing_info": {
                    "first_name": "test",
                    "last_name": "test",
                    "address1": "test",
                    "city": "test",
                    "state": "test",
                    "zip": "test",
                    "country": "test",
                    "phone": "test",
                    "email": "test",
                    "company": "test",
                    "address2": "test",
                    "fax": "test",
                    "shipping_id": "test",
                    "shipping_address1": "test",
                    "shipping_address2": "test",
                    "shipping_city": "test",
                    "shipping_country": "test",
                    "shipping_zip": "test",
                    "shipping_state": "test",
                    "shipping_first_name": "test",
                    "shipping_last_name": "test",
                    "shipping_phone": "test",
                    "shipping_email": "test",
                },
            }
        )

        print(result)
        self.assertEqual(result["status_code"], 200)
        self.assertEqual(result["response"]["nm_response"]["response_code"], "100")

    def test_update_billing_info(self):
        billing = Billing(url="http://127.0.0.1:8000", org="testOrg4")
        result = billing.update_billing_info(
            {
                "user_id": "1",
                "billing_id": "15",
                "org": "testOrg4",
                "token": "00000000-000000-000000-000000000000",
                "billing_info": {
                    "first_name": "Carlos",
                    "last_name": "test",
                    "address1": "test",
                    "city": "test",
                    "state": "test",
                    "zip": "test",
                    "country": "test",
                    "phone": "test",
                    "email": "test",
                    "company": "test",
                    "address2": "test",
                    "fax": "test",
                    "shipping_id": "test",
                    "shipping_address1": "test",
                    "shipping_address2": "test",
                    "shipping_city": "test",
                    "shipping_country": "test",
                    "shipping_zip": "test",
                    "shipping_state": "test",
                    "shipping_first_name": "test",
                    "shipping_last_name": "test",
                    "shipping_phone": "test",
                    "shipping_email": "test",
                },
            }
        )

        print(result)
        self.assertEqual(result["status_code"], 200)
        self.assertEqual(result["response"]["nm_response"]["response_code"], "100")

    def test_delete(self):
        billing = Billing(url="http://127.0.0.1:8000", org="testOrg4")
        result = billing.delete(
            org="testOrg4",
            user_id="1",
            billing_id="15",
        )
        print(result)
        self.assertEqual(result["status_code"], 200)
        self.assertEqual(result["response"]["nm_response"]["response_code"], "100")

    def test_set_priority(self):
        billing = Billing(url="http://127.0.0.1:8000", org="testOrg4")
        result = billing.set_priority(
            {"user_id": "1", "org": "testOrg4", "billing_id": "16", "priority": 1}
        )
        print(result)
        self.assertEqual(result["status_code"], 200)
        self.assertEqual(result["response"]["nm_response"]["response_code"], "100")

    def test_info(self):
        billing = Billing(url="http://127.0.0.1:8000", org="testOrg4")
        result = billing.info(org="testOrg4", user_id="1")
        self.assertEqual(result["status_code"], 200)
        self.assertGreaterEqual(len(result["response"]), 0)

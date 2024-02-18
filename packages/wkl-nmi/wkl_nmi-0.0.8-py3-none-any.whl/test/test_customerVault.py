import unittest
from unittest.mock import patch
from wknmi.customer_vault import CustomerVault


class TestCustomerVault(unittest.TestCase):
    def test_add(self):
        customerVault = CustomerVault(url="http://127.0.0.1:8000", org="testOrg4")
        result = customerVault.add(
            {
                "id": "testId113233",
                "token": "00000000-000000-000000-000000000000",
                "billing_id": "",
                "billing_info": {
                    "first_name": "",
                    "last_name": "",
                    "address1": "",
                    "city": "",
                    "state": "",
                    "zip": "",
                    "country": "",
                    "phone": "",
                    "email": "",
                },
            }
        )
        self.assertEqual(result["status_code"], 200)
        self.assertEqual(result["response"]["nm_response"]["response_code"], "100")

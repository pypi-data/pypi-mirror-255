import unittest
from unittest.mock import patch
from wknmi.subscriptions import Subscriptions


class TestSubscriptions(unittest.TestCase):
    def test_add_with_custom_month_frequency_config(self):
        subsObj = Subscriptions(url="http://127.0.0.1:8000", org="testOrg4")
        result = subsObj.add_with_custom_month_frequency_config(
            {
                "user_id": "1",
                "order_id": "test",
                "total_amount": "0",  # 0 for subscription without an addition sale amount
                "custom_subscription_info": {
                    "plan_id": "test",
                    "plan_amount": "10.00",
                    "plan_name": "test",
                    "month_frequency": "1",
                    "day_of_month": "1",
                    "plan_payments": "0",
                },
            }
        )
        self.assertEqual(result["status_code"], 200)
        self.assertEqual(result["response"]["nm_response"]["response_code"], "100")

    def test_edit_with_custom_month_frequency_config(self):
        subsObj = Subscriptions(url="http://127.0.0.1:8000", org="testOrg4")
        result = subsObj.add_with_custom_day_frequency_config(
            {
                "user_id": "1",
                "org": "testOrg",
                "order_id": "testRef",
                "total_amount": "0",  # 0 for subscription without an addition sale amount
                "custom_subscription_info": {
                    "plan_payments": "15",
                    "plan_amount": "6",
                    "day_frequency": "1",
                },
            }
        )
        self.assertEqual(result["status_code"], 200)
        self.assertEqual(result["response"]["nm_response"]["response_code"], "100")

    def test_pause(self):
        subsObj = Subscriptions(url="http://127.0.0.1:8000", org="testOrg4")
        result = subsObj.pause("8963837207", "true")
        self.assertEqual(result["status_code"], 200)

    def test_cancel(self):
        subsObj = Subscriptions(url="http://127.0.0.1:8000", org="testOrg4")
        result = subsObj.cancel("8963837207")
        self.assertEqual(result["status_code"], 200)

    def test_by_user_id(self):
        subsObj = Subscriptions(url="http://127.0.0.1:8000", org="testOrg4")
        result = subsObj.by_user_id("1")
        print(result)
        self.assertEqual(result["status_code"], 200)

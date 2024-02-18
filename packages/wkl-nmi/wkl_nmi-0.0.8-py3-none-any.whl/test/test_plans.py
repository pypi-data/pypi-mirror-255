import unittest
from unittest.mock import patch
from wknmi.plans import Plans


class TestPlans(unittest.TestCase):
    def test_all(self):
        plan = Plans(url="http://127.0.0.1:8000", org="testOrg4")
        plans = plan.all()
        print(plans)
        self.assertGreater(len(plans), 0)

    def test_id(self):
        plan = Plans(url="http://127.0.0.1:8000", org="testOrg4")
        plan = plan.id("swzshoppingonly")
        self.assertEqual(plan["plan_id"], "swzshoppingonly")

    def test_add_month_configuration(self):
        plan = Plans(url="http://127.0.0.1:8000", org="testOrg4")
        result = plan.add_month_configuration(
            {
                "custom_plan": {
                    "plan_amount": "10.00",
                    "plan_name": "test",
                    "plan_id": "testtset",
                    "month_frequency": "1",
                    "day_of_month": "1",
                    "plan_payments": "0",
                }
            }
        )
        self.assertEqual(result["status_code"], 200)

    def test_edit_month_configuration(self):
        plan = Plans(url="http://127.0.0.1:8000", org="testOrg4")
        result = plan.edit_month_configuration(
            {
                "custom_plan": {
                    "plan_amount": "10.00",
                    "plan_name": "test",
                    "plan_id": "testtset",
                    "month_frequency": "1",
                    "day_of_month": "1",
                    "plan_payments": "0",
                }
            }
        )
        self.assertEqual(result["status_code"], 200)

    def test_add_day_configuration(self):
        plan = Plans(url="http://127.0.0.1:8000", org="testOrg4")
        result = plan.add_day_configuration(
            {
                "custom_plan": {
                    "plan_amount": "10.00",
                    "plan_name": "test",
                    "plan_id": "testtsetts",
                    "day_frequency": "1",
                    "plan_payments": "0",
                }
            }
        )
        self.assertEqual(result["status_code"], 200)

    def test_edit_day_configuration(self):
        plan = Plans(url="http://127.0.0.1:8000", org="testOrg4")
        result = plan.edit_day_configuration(
            {
                "custom_plan": {
                    "plan_amount": "20.00",
                    "plan_name": "test",
                    "plan_id": "testtsetts",
                    "day_frequency": "1",
                    "plan_payments": "0",
                }
            }
        )
        print(result)
        self.assertEqual(result["status_code"], 200)

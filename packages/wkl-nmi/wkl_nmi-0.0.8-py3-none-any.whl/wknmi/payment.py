from wknmi.auth import get_id_token
import requests


class Pay:
    def __init__(self, url, org):
        self.url = url
        self.org = org

    def with_token(self, body):
        """with token"""
        _token_id = get_id_token(self.url)
        headers = {"Authorization": "Bearer " + _token_id}
        body["org"] = self.org
        response = requests.post(
            f"{self.url}/payment/with-token",
            headers=headers,
            json=body,
        )
        if response.status_code == 200:
            return {"response": response.json(), "status_code": response.status_code}
        else:
            return {"response": response.json(), "status_code": response.status_code}

    def with_customer_vault(self, body):
        """Pay with customer vault"""
        _token_id = get_id_token(self.url)
        headers = {"Authorization": "Bearer " + _token_id}
        body["org"] = self.org
        print(body)
        response = requests.post(
            f"{self.url}/payment/with-customer-vault",
            headers=headers,
            json=body,
        )
        if response.status_code == 200:
            return {"response": response.json(), "status_code": response.status_code}
        else:
            return {"response": response.json(), "status_code": response.status_code}

    def refund(self, transaction_id: str):
        """Refund"""
        _token_id = get_id_token(self.url)
        headers = {"Authorization": "Bearer " + _token_id}
        response = requests.post(
            f"{self.url}/payment/refund?org={self.org}&transaction_id={transaction_id}",
            headers=headers,
        )
        if response.status_code == 200:
            return {"response": response.json(), "status_code": response.status_code}
        else:
            return {"response": response.json(), "status_code": response.status_code}

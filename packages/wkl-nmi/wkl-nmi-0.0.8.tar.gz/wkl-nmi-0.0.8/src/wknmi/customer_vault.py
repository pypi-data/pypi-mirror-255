from wknmi.auth import get_id_token
import requests


class CustomerVault:
    def __init__(self, url, org):
        self.url = url
        self.org = org

    def add(self, body):
        _token_id = get_id_token(self.url)
        headers = {"Authorization": "Bearer " + _token_id}
        body["org"] = self.org
        response = requests.post(
            f"{self.url}/customer-vault/add", headers=headers, json=body
        )
        if response.status_code == 200:
            return {"response": response.json(), "status_code": response.status_code}
        else:
            return {"response": response.json(), "status_code": response.status_code}

    def edit(self, body):
        _token_id = get_id_token(self.url)
        headers = {"Authorization": "Bearer " + _token_id}
        body["org"] = self.org
        response = requests.put(
            f"{self.url}/customer-vault/edit", headers=headers, json=body
        )
        if response.status_code == 200:
            return {"response": response.json(), "status_code": response.status_code}
        else:
            return {"response": response.json(), "status_code": response.status_code}

    def delete(self, id: str):
        _token_id = get_id_token(self.url)
        headers = {"Authorization": "Bearer " + _token_id}
        response = requests.delete(
            f"{self.url}/customer-vault/delete?org={self.org}&id={id}", headers=headers
        )
        if response.status_code == 200:
            return {"response": response.json(), "status_code": response.status_code}
        else:
            return {"response": response.json(), "status_code": response.status_code}

from wknmi.auth import get_id_token
import requests 

class Billing():
    def __init__(self, url, org):
        self.url = url
        self.org = org

    def add(self, body):
        """add billing id """
        _token_id = get_id_token(self.url)
        headers = {'Authorization': 'Bearer ' + _token_id}
        response = requests.post(f'{self.url}/billing/add', headers=headers, json=body)
        return {"response": response.json(), "status_code": response.status_code}
    
    def update_billing_info(self, body):
        """update billing id """
        _token_id = get_id_token(self.url)
        headers = {'Authorization': 'Bearer ' + _token_id}
        response = requests.put(f'{self.url}/billing/update-billing-info', headers=headers, json=body)
        return {"response": response.json(), "status_code": response.status_code}
        
    def delete(self, org, user_id, billing_id):
        """delete billing id """
        _token_id = get_id_token(self.url)
        headers = {'Authorization': 'Bearer ' + _token_id}
        response = requests.delete(f'{self.url}/billing/delete?org={org}&user_id={user_id}&billing_id={billing_id}', headers=headers)
        return {"response": response.json(), "status_code": response.status_code}
    
    def set_priority(self, body):
        """change billing id priority"""
        _token_id = get_id_token(self.url)
        headers = {'Authorization': 'Bearer ' + _token_id}
        response = requests.put(f'{self.url}/billing/change-priority', headers=headers, json=body)
        return {"response": response.json(), "status_code": response.status_code}
    

    def info(self, org, user_id):
        """get billing info"""
        _token_id = get_id_token(self.url)
        headers = {'Authorization': 'Bearer ' + _token_id}
        response = requests.get(f'{self.url}/billing/billing-of-user?org={org}&user_id={user_id}', headers=headers)
        return {"response": response.json(), "status_code": response.status_code}
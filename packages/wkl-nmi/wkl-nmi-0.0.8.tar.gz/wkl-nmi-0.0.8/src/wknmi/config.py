from wknmi.auth import get_id_token
import requests 

class Config():
    def __init__(self, url, org):
        self.url = url
        self.org = org

    def get(self):
        """Get client by id"""
        _token_id = get_id_token(self.url)
        headers = {'Authorization': 'Bearer ' + _token_id}
        response = requests.get(f'{self.url}/configs/get-config?org={self.org}', headers=headers)
        return response.json()
    
    
    def update(self, body):
        """Update client by id"""
        _token_id = get_id_token(self.url)
        headers = {'Authorization': 'Bearer ' + _token_id}
        response = requests.put(f'{self.url}/configs/update-config?org={self.org}', headers=headers, json=body)
        return response.json()
    
    def add(self, body):
        """Add new client"""
        _token_id = get_id_token(self.url)
        headers = {'Authorization': 'Bearer ' + _token_id}
        response = requests.post(f'{self.url}/configs/add-config', headers=headers, json=body)
        return response.json()

    
    def delete(self, org):
        """Delete client by id"""
        _token_id = get_id_token(self.url)
        headers = {'Authorization': 'Bearer ' + _token_id}
        response = requests.delete(f'{self.url}/configs/delete-config?org={org}', headers=headers)
        return response.json()
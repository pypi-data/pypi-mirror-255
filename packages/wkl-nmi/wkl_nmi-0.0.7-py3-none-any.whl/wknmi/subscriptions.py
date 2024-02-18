from wknmi.auth import get_id_token
import requests 


class Subscriptions():
    def __init__(self, url, org):
        self.url = url
        self.org = org
    
    def all(self):
        """Get all subscriptions"""
        _token_id = get_id_token(self.url)
        headers = {'Authorization': 'Bearer ' + _token_id}
        response = requests.get(self.url + '/subscriptions', headers=headers)
        return response.json()
    
    
    def add_with_custom_month_frequency_config(self, body):
        """Add a subscription with custom month frequency config"""
        _token_id = get_id_token(self.url)
        headers = {'Authorization': 'Bearer ' + _token_id}
        body['org'] = self.org
        response = requests.post(f'{self.url}/subscriptions/month-frequency-config', headers=headers, json=body)
        if (response.status_code == 200):
            return {"response":response.json(), "status_code":response.status_code}
        else:
            return {"response":response.json(), "status_code":response.status_code}
    
    def add_with_custom_day_frequency_config(self, body):
        """Add a subscription with custom day frequency config"""
        _token_id = get_id_token(self.url)
        headers = {'Authorization': 'Bearer ' + _token_id}
        body['org'] = self.org
        response = requests.post(f'{self.url}/subscriptions/day-frequency-config', headers=headers, json=body)
        if (response.status_code == 200):
            return {"response":response.json(), "status_code":response.status_code}
        else:
            return {"response":response.json(), "status_code":response.status_code}


    def pause(self, subscription_id, pause):
        """Pause a subscription"""
        _token_id = get_id_token(self.url)
        headers = {'Authorization': 'Bearer ' + _token_id}
        response = requests.put(f'{self.url}/subscriptions/pause?org={self.org}&subscription_id={subscription_id}&pause={pause}', headers=headers)
        if (response.status_code == 200):
            return {"response":response.json(), "status_code":response.status_code}
        else:
            return {"response":response.json(), "status_code":response.status_code}
        

    def cancel(self, subscription_id):
        """Pause a subscription"""
        _token_id = get_id_token(self.url)
        headers = {'Authorization': 'Bearer ' + _token_id}
        response = requests.delete(f'{self.url}/subscriptions/cancel-subscription?org={self.org}&subscription_id={subscription_id}', headers=headers)
        if (response.status_code == 200):
            return {"response":response.json(), "status_code":response.status_code}
        else:
            return {"response":response.json(), "status_code":response.status_code}
    

    def id(self, user_id):
        """Get subscriptions by user id"""
        _token_id = get_id_token(self.url)
        headers = {'Authorization': 'Bearer ' + _token_id}
        response = requests.get(f'{self.url}/subscriptions/by-user-id?org={self.org}&user_id={user_id}', headers=headers)
        if (response.status_code == 200):
            return {"response":response.json(), "status_code":response.status_code}
        else:
            return {"response":response.json(), "status_code":response.status_code}



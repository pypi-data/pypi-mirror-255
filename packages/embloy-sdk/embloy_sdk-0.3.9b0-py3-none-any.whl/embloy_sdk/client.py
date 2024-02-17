import requests
import json

class EmbloyClient:
    def __init__(self, client_token, session, base_url='https://api.embloy.com', api_version='api/v0'):
        self.client_token = client_token
        self.session = session
        self.base_url = base_url
        self.api_version = api_version

    def make_request(self):
        url = f'{self.base_url}/{self.api_version}/sdk/request/auth/token'
        headers = {'client_token': self.client_token}
        data = {
            'mode': self.session.get('mode', 'job'),
            'success_url': self.session.get('success_url', ''),
            'cancel_url': self.session.get('cancel_url', ''),
            'job_slug': self.session.get('job_slug', '')
        }

        try:
            response = requests.post(url, headers=headers, data=data)
            response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
            return self.handle_response(response)
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error making request: {str(e)}")

    def handle_response(self, response):
        if response.status_code == 200:
            request_token = json.loads(response.text)['request_token']
            return f"@{self.base_url}/sdk/apply?token={request_token}"
        else:
            raise Exception(f"Error making request: {response.text}")


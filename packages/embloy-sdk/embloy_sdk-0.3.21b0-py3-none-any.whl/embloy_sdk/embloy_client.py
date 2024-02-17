import requests
import json

class EmbloyClient:
    def __init__(self, client_token, session, api_url='https://api.embloy.com', base_url='https://embloy.com', api_version='api/v0'):
        if not isinstance(client_token, str):
            raise ValueError('client_token must be a string')
        self.client_token = client_token
        self.session = session
        self.api_url = api_url
        self.base_url = base_url
        self.api_version = api_version

    def form_request(self):
        data = {
            'mode': self.session.mode,
            'job_slug': self.session.job_slug,
        }

        if self.session.success_url is not None:
            data['success_url'] = self.session.success_url

        if self.session.cancel_url is not None:
            data['cancel_url'] = self.session.cancel_url

        headers = {
            'client_token': self.client_token,
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:122.0) Gecko/20100101 Firefox/122.0',
        }

        return data, headers

    def make_request(self):
        data, headers = self.form_request()

        payload = json.dumps({
        "mode": "job",
        "job_slug": "test123",
        "success_url": "https://example.com/success",
        "cancel_url": "https://example.com/cancel"
        })

        try:
            response = requests.post(f'{self.api_url}/{self.api_version}/sdk/request/auth/token', headers=headers, data=payload)
            response.raise_for_status()
            request_token = response.json()['request_token']
            return f"{self.base_url}/sdk/apply?request_token={request_token}"
        except requests.exceptions.RequestException as e:
            debug_info = {
                'client_token': self.client_token,
                'error': str(e),
                'request_headers': headers,
                'response_headers': dict(response.headers),
            }
            print('Debug Info:', debug_info)
            raise e
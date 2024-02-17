import requests

class EmbloyClient:
    def __init__(self, client_token, session, api_url='https://api.embloy.com', base_url='https://embloy.com', api_version='api/v0'):
        if not isinstance(client_token, str):
            raise ValueError('clientToken must be a string')
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
            'Content-Type': 'application/json',
            'client_token': self.client_token,
            'User-Agent': 'embloy/0.1.2-beta.20 (Python; Client)',
            'Content-Type': 'application/json',
            'HTTP_CLIENT_TOKEN': self.client_token,
            'User-Agent': 'embloy/0.1.2-beta.20 (Python; Client)',
            'DNT': '1',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-GPC': '1',
            'TE': 'trailers',
            'Origin': 'https://api.example.com',
        }

        return data, headers

    def make_request(self):
        data, headers = self.form_request()

        try:
            response = requests.post(f'{self.api_url}/{self.api_version}/sdk/request/auth/token', json=data, headers=headers)
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
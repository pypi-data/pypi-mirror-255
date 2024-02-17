import requests

class EmbloyClient:
    """
    A class used to represent a client for the Embloy API.

    Attributes
    ----------
    client_token : str
        The client token for the API.
    session : EmbloySession
        The session associated with the client.
    api_url : str
        The URL for the API.
    base_url : str
        The base URL for the API.
    api_version : str
        The version of the API.

    Methods
    -------
    get_form_data_and_headers()
        Returns the form data and headers for a request.
    make_request()
        Makes a request to the API and returns a URL with the request token.
    """
    def __init__(self, client_token, session, api_url='https://api.embloy.com', base_url='https://embloy.com', api_version='api/v0'):
        if not isinstance(client_token, str):
            raise ValueError('clientToken must be a string')
        self.client_token = client_token
        self.session = session
        self.api_url = api_url
        self.base_url = base_url
        self.api_version = api_version

    def get_form_data_and_headers(self):
        """
        Returns the form data and headers for a request.

        Returns
        -------
        tuple
            A tuple containing the form data and headers.
        """
        data = {
            'mode': self.session.mode,
            'job_slug': self.session.job_slug,
            'success_url': self.session.success_url,
            'cancel_url': self.session.cancel_url,
        }

        headers = {
            'client_token': self.client_token,
            'User-Agent': 'embloy-sdk/0.3.1b (Python; Server)',
            'Content-Type': 'application/json',
        }

        return data, headers

    def make_request(self):
        """
        Makes a request to the API and returns a URL with the request token.

        Returns
        -------
        str
            A URL with the request token for the application session.

        Raises
        ------
        requests.exceptions.RequestException
            If the request fails for any reason.
        """
        data, headers = self.get_form_data_and_headers()

        try:
            response = requests.post(f'{self.api_url}/{self.api_version}/sdk/request/auth/token', json=data, headers=headers)
            response.raise_for_status()
            request_token = response.json()['request_token']
            return f"{self.base_url}/sdk/apply?request_token={request_token}"
        except requests.exceptions.RequestException as e:
            raise e
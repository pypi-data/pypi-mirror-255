import unittest
import json
from unittest.mock import patch, Mock
from embloy_sdk import EmbloyClient, EmbloySession

class TestEmbloyClient(unittest.TestCase):
    @patch('requests.request')
    def test_make_request(self, mock_request):
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {'request_token': 'test_token'}
        mock_request.return_value = mock_response

        session = EmbloySession('test_mode', 'test_job_slug')
        client = EmbloyClient('test_token', session)

        result = client.make_request()

        self.assertEqual(result, 'https://embloy.com/sdk/apply?request_token=test_token')
        mock_request.assert_called_once_with(
            "POST",
            'https://api.embloy.com/api/v0/sdk/request/auth/token',
            headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:122.0) Gecko/20100101 Firefox/122.0', 'client_token': 'test_token', 'Content-Type': 'application/json'},
            data=json.dumps({'mode': 'test_mode', 'job_slug': 'test_job_slug'})
        )

if __name__ == '__main__':
    unittest.main()
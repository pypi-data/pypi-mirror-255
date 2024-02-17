import unittest
from unittest.mock import patch, Mock
from embloy_sdk import EmbloyClient, EmbloySession

class TestEmbloyClient(unittest.TestCase):
    @patch('requests.post')
    def test_make_request(self, mock_post):
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {'request_token': 'test_token'}
        mock_post.return_value = mock_response

        session = EmbloySession('test_mode', 'test_job_slug')
        client = EmbloyClient('test_token', session)

        result = client.make_request()

        self.assertEqual(result, 'https://embloy.com/sdk/apply?request_token=test_token')
        mock_post.assert_called_once_with(
            'https://api.embloy.com/api/v0/sdk/request/auth/token',
            json={'mode': 'test_mode', 'job_slug': 'test_job_slug'},
            headers={'User-Agent': 'embloy/0.1.2-beta.20 (Python; Server)', 'client_token': 'test_token', 'Content-Type': 'application/json'}
        )

if __name__ == '__main__':
    unittest.main()
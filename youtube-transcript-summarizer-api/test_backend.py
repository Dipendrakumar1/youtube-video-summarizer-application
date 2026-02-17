import unittest
from app import app
import json

class TestBackendAPI(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_root_route(self):
        response = self.app.get('/')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['message'], 'Success')

    def test_api_missing_url(self):
        response = self.app.get('/api/')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['status'], 'Failed')

    # Note: Creating a full integration test calling YouTube API might be flaky 
    # and slow, so we test the structure primarily.
    # To test actual summarization, we would need to mock the external calls, 
    # but for this verification, ensuring the app imports and routes work is key.

if __name__ == '__main__':
    unittest.main()

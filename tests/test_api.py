import unittest
import sys
import os

# Add app folder to path
sys.path.append('app')

from main import app
from fastapi.testclient import TestClient

class TestLibraryAPI(unittest.TestCase):
    
    def setUp(self):
        self.client = TestClient(app)
    
    def test_items_endpoint(self):
        response = self.client.get("/items")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertTrue(isinstance(data, list))
        self.assertTrue(len(data) > 0)
    
    def test_health_endpoint(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data, {"status": "ok"})

if __name__ == "__main__":
    unittest.main()

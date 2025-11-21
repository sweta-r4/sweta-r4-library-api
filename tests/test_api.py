import unittest
import sys
import os
import json

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.main import app, db_manager
from fastapi.testclient import TestClient

class TestLibraryAPI(unittest.TestCase):
    
    def setUp(self):
        self.client = TestClient(app)
        # Clear database before each test
        db_manager.clear_database()
    
    def tearDown(self):
        # Clear database after each test
        db_manager.clear_database()
    
    def test_database_connection(self):
        """Test database connectivity"""
        conn = db_manager.get_connection()
        self.assertIsNotNone(conn)
        conn.close()
    
    def test_root_endpoint(self):
        """Test root endpoint"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("message", data)
        self.assertEqual(data["message"], "Library Management System API")
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "healthy")
    
    def test_books_crud_operations(self):
        """Test complete CRUD operations for books"""
        # Test GET all books (empty initially due to clear_database)
        response = self.client.get("/books")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 0)  # Should be empty now
        
        # Test POST new book
        book_data = {
            "title": "Test Book",
            "author": "Test Author",
            "genre": "Fiction",
            "stock": 5
        }
        response = self.client.post("/books", json=book_data)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["message"], "Book created successfully")
        self.assertEqual(data["book"]["title"], "Test Book")
        
        # Test GET all books (should have one now)
        response = self.client.get("/books")
        self.assertEqual(response.status_code, 200)
        books = response.json()
        self.assertEqual(len(books), 1)
        
        # Test GET specific book
        book_id = books[0]["book_id"]
        response = self.client.get(f"/books/{book_id}")
        self.assertEqual(response.status_code, 200)
        book = response.json()
        self.assertEqual(book["title"], "Test Book")
        
        # Test PUT update book
        update_data = {
            "title": "Updated Book",
            "stock": 10
        }
        response = self.client.put(f"/books/{book_id}", json=update_data)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["book"]["title"], "Updated Book")
        self.assertEqual(data["book"]["stock"], 10)
        
        # Test DELETE book
        response = self.client.delete(f"/books/{book_id}")
        self.assertEqual(response.status_code, 200)
        
        # Verify book is deleted
        response = self.client.get(f"/books/{book_id}")
        self.assertEqual(response.status_code, 404)
    
    def test_advanced_json_operations(self):
        """Test advanced JSON handling with nested structures"""
        # Test advanced book creation
        advanced_book_data = {
            "title": "Advanced Book",
            "author": "Advanced Author",
            "details": {
                "genre": "Science Fiction",
                "stock": 15
            }
        }
        
        response = self.client.post("/books/advanced", json=advanced_book_data)
        self.assertEqual(response.status_code, 200)
        book = response.json()
        
        self.assertEqual(book["title"], "Advanced Book")
        self.assertIn("details", book)
        self.assertEqual(book["details"]["genre"], "Science Fiction")
        self.assertEqual(book["details"]["stock"], 15)
        
        # Test advanced book retrieval
        book_id = book["book_id"]
        response = self.client.get(f"/books/advanced/{book_id}")
        self.assertEqual(response.status_code, 200)
        retrieved_book = response.json()
        
        self.assertEqual(retrieved_book["title"], "Advanced Book")
        self.assertIn("details", retrieved_book)
    
    def test_json_validation(self):
        """Test JSON validation endpoints"""
        # Test valid book JSON
        valid_book_json = {
            "title": "Valid Book",
            "author": "Valid Author",
            "details": {
                "genre": "Mystery",
                "stock": 5
            }
        }
        
        response = self.client.post("/validate/book", json=valid_book_json)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["valid"])
        
        # Test invalid book JSON (missing title)
        invalid_book_json = {
            "author": "Invalid Author",
            "details": {
                "genre": "Mystery"
            }
        }
        
        response = self.client.post("/validate/book", json=invalid_book_json)
        self.assertEqual(response.status_code, 400)
    
    def test_error_handling(self):
        """Test error cases"""
        # Test getting non-existent book
        response = self.client.get("/books/999")
        self.assertEqual(response.status_code, 404)
        
        # Test updating non-existent book
        response = self.client.put("/books/999", json={"title": "Test"})
        self.assertEqual(response.status_code, 404)
        
        # Test deleting non-existent book
        response = self.client.delete("/books/999")
        self.assertEqual(response.status_code, 404)
        
        # Test invalid JSON in validation
        response = self.client.post("/validate/book", json={"invalid": "data"})
        self.assertEqual(response.status_code, 400)

if __name__ == "__main__":
    unittest.main()
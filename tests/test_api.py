import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.main import app
from fastapi.testclient import TestClient

class TestLibraryAPI(unittest.TestCase):
    
    def setUp(self):
        self.client = TestClient(app)
    
    def test_home_endpoint(self):
        """Test the home endpoint"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data["message"], "Library Management System")
    
    def test_items_endpoint(self):
        """Test the items endpoint returns books"""
        response = self.client.get("/items")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertTrue(isinstance(data, list))
        self.assertTrue(len(data) > 0)
    
    def test_health_endpoint(self):
        """Test the health endpoint"""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data["status"], "ok")
        self.assertIn("request_counts", data)
        self.assertIn("total_errors", data)
    
    def test_books_crud_operations(self):
        """Test CRUD operations for books"""
        # Test GET all books
        response = self.client.get("/books")
        self.assertEqual(response.status_code, 200)
        initial_books = response.json()
        
        # Test POST new book
        new_book_data = {"title": "Test Book", "author": "Test Author"}
        response = self.client.post("/books", params=new_book_data)
        self.assertEqual(response.status_code, 200)
        
        # Test GET all books after addition
        response = self.client.get("/books")
        self.assertEqual(response.status_code, 200)
        updated_books = response.json()
        self.assertEqual(len(updated_books), len(initial_books) + 1)
        
        # Test PUT update book
        book_id = updated_books[-1]["id"]
        update_data = {"title": "Updated Book", "author": "Updated Author"}
        response = self.client.put(f"/books/{book_id}", params=update_data)
        self.assertEqual(response.status_code, 200)
        
        # Test DELETE book
        response = self.client.delete(f"/books/{book_id}")
        self.assertEqual(response.status_code, 200)
    
    def test_readers_crud_operations(self):
        """Test CRUD operations for readers"""
        # Test GET all readers
        response = self.client.get("/readers")
        self.assertEqual(response.status_code, 200)
        
        # Test POST new reader
        new_reader_data = {"name": "John Doe", "membership_id": "MEM123"}
        response = self.client.post("/readers", params=new_reader_data)
        self.assertEqual(response.status_code, 200)
        
        # Test PUT update reader
        readers = self.client.get("/readers").json()
        if readers:
            reader_id = readers[-1]["id"]
            update_data = {"name": "Jane Doe", "membership_id": "MEM456"}
            response = self.client.put(f"/readers/{reader_id}", params=update_data)
            self.assertEqual(response.status_code, 200)
    
    def test_staff_crud_operations(self):
        """Test CRUD operations for staff"""
        # Test GET all staff
        response = self.client.get("/staff")
        self.assertEqual(response.status_code, 200)
        
        # Test POST new staff
        new_staff_data = {"name": "Jane Smith", "position": "Librarian"}
        response = self.client.post("/staff", params=new_staff_data)
        self.assertEqual(response.status_code, 200)
        
        # Test PUT update staff
        staff_members = self.client.get("/staff").json()
        if staff_members:
            staff_id = staff_members[-1]["id"]
            update_data = {"name": "John Smith", "position": "Senior Librarian"}
            response = self.client.put(f"/staff/{staff_id}", params=update_data)
            self.assertEqual(response.status_code, 200)
    
    def test_error_cases(self):
        """Test error cases"""
        # Test updating non-existent book
        response = self.client.put("/books/999", params={"title": "Test", "author": "Test"})
        self.assertEqual(response.status_code, 404)
        
        # Test deleting non-existent book
        response = self.client.delete("/books/999")
        self.assertEqual(response.status_code, 404)
        
        # Test adding book with missing parameters
        response = self.client.post("/books", params={"title": ""})
        self.assertEqual(response.status_code, 400)

if __name__ == "__main__":
    unittest.main()
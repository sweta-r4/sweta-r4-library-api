import unittest
import os
import sys

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.main import db_manager

class TestDatabase(unittest.TestCase):
    
    def setUp(self):
        # Clear database before each test
        db_manager.clear_database()
    
    def tearDown(self):
        # Clear database after each test
        db_manager.clear_database()
    
    def test_database_initialization(self):
        """Test that database tables are created properly"""
        # Test books table
        books = db_manager.execute_query("SELECT name FROM sqlite_master WHERE type='table' AND name='books'")
        self.assertEqual(len(books), 1)
        
        # Test staff table
        staff = db_manager.execute_query("SELECT name FROM sqlite_master WHERE type='table' AND name='staff'")
        self.assertEqual(len(staff), 1)
        
        # Test readers table
        readers = db_manager.execute_query("SELECT name FROM sqlite_master WHERE type='table' AND name='readers'")
        self.assertEqual(len(readers), 1)
    
    def test_database_operations(self):
        """Test basic database operations"""
        # Test INSERT
        book_id = db_manager.execute_update(
            "INSERT INTO books (title, author, genre, stock) VALUES (?, ?, ?, ?)",
            ("Test Book", "Test Author", "Fiction", 5)
        )
        self.assertIsNotNone(book_id)
        
        # Test SELECT
        books = db_manager.execute_query("SELECT * FROM books WHERE book_id = ?", (book_id,))
        self.assertEqual(len(books), 1)
        self.assertEqual(books[0]["title"], "Test Book")
        
        # Test UPDATE
        db_manager.execute_update(
            "UPDATE books SET stock = ? WHERE book_id = ?",
            (10, book_id)
        )
        
        updated_book = db_manager.execute_query("SELECT * FROM books WHERE book_id = ?", (book_id,))
        self.assertEqual(updated_book[0]["stock"], 10)
        
        # Test DELETE
        db_manager.execute_update("DELETE FROM books WHERE book_id = ?", (book_id,))
        remaining_books = db_manager.execute_query("SELECT * FROM books WHERE book_id = ?", (book_id,))
        self.assertEqual(len(remaining_books), 0)

if __name__ == "__main__":
    unittest.main()
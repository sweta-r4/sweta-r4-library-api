# app/database.py
import sqlite3
import os
from typing import List, Dict, Any

class DatabaseManager:
    def __init__(self, db_name: str = "library.db"):
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_dir = os.path.join(self.current_dir, "data")
        self.db_path = os.path.join(self.data_dir, db_name)
        
        # Create data directory if it doesn't exist
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.init_database()
    
    def get_connection(self) -> sqlite3.Connection:
        """Get a database connection"""
        return sqlite3.connect(self.db_path)
    
    def init_database(self) -> None:
        """Initialize database with required tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Books table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS books (
                book_id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                genre TEXT,
                stock INTEGER DEFAULT 1
            )
        ''')
        
        # Staff table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS staff (
                staff_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                role TEXT NOT NULL,
                contact TEXT
            )
        ''')
        
        # Readers table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS readers (
                reader_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                contact TEXT,
                borrowed_books TEXT DEFAULT '[]'
            )
        ''')
        
        conn.commit()
        conn.close()
        print("Database initialized successfully!")
    
    def execute_query(self, query: str, params: tuple = ()) -> List[Dict]:
        """Execute a query and return results as dictionaries"""
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(query, params)
        results = [dict(row) for row in cursor.fetchall()]
        
        conn.commit()
        conn.close()
        return results
    
    def execute_update(self, query: str, params: tuple = ()) -> int:
        """Execute an update query and return last row ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(query, params)
        conn.commit()
        last_id = cursor.lastrowid
        
        conn.close()
        return last_id

# Global database instance
db_manager = DatabaseManager()
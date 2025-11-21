from fastapi import FastAPI, HTTPException, status, Depends
from typing import List, Dict, Optional
import logging
import os
import sqlite3
import json
from datetime import datetime
from pydantic import BaseModel, validator

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

# Database Manager
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
        logging.info("Database initialized successfully!")
    
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

    def clear_database(self) -> None:
        """Clear all data from tables (for testing)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM books")
        cursor.execute("DELETE FROM staff")
        cursor.execute("DELETE FROM readers")
        
        conn.commit()
        conn.close()
        logging.info("Database cleared for testing")

# Global database instance
db_manager = DatabaseManager()

# Pydantic Models for Basic CRUD Operations
class BookBase(BaseModel):
    title: str
    author: str
    genre: Optional[str] = None
    stock: Optional[int] = 1

class BookCreate(BookBase):
    pass

class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    genre: Optional[str] = None
    stock: Optional[int] = None

class BookResponse(BookBase):
    book_id: int
    
    class Config:
        from_attributes = True

class StaffBase(BaseModel):
    name: str
    role: str
    contact: Optional[str] = None

class StaffCreate(StaffBase):
    pass

class StaffUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    contact: Optional[str] = None

class StaffResponse(StaffBase):
    staff_id: int
    
    class Config:
        from_attributes = True

class ReaderBase(BaseModel):
    name: str
    contact: Optional[str] = None

class ReaderCreate(ReaderBase):
    pass

class ReaderUpdate(BaseModel):
    name: Optional[str] = None
    contact: Optional[str] = None

class ReaderResponse(ReaderBase):
    reader_id: int
    borrowed_books: List[int] = []
    
    class Config:
        from_attributes = True

# Advanced JSON Models for Nested Structures
class BookDetails(BaseModel):
    genre: Optional[str] = None
    stock: Optional[int] = 1

class BookAdvancedCreate(BaseModel):
    title: str
    author: str
    details: BookDetails
    
    @validator('title')
    def title_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Title cannot be empty')
        return v.strip()
    
    @validator('author')
    def author_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Author cannot be empty')
        return v.strip()

class BookAdvancedResponse(BaseModel):
    book_id: int
    title: str
    author: str
    details: BookDetails

class ReaderDetails(BaseModel):
    contact: Optional[str] = None
    borrowed_books: List[int] = []

class ReaderAdvancedCreate(BaseModel):
    name: str
    details: ReaderDetails

class ReaderAdvancedResponse(BaseModel):
    reader_id: int
    name: str
    details: ReaderDetails

# JSON Validation Functions
def validate_book_json(json_data: Dict) -> tuple:
    """Validate book JSON payload for advanced endpoints"""
    try:
        book = BookAdvancedCreate(**json_data)
        return True, book.model_dump()  # Fixed: using model_dump() instead of dict()
    except Exception as e:
        return False, str(e)

def validate_reader_json(json_data: Dict) -> tuple:
    """Validate reader JSON payload for advanced endpoints"""
    try:
        reader = ReaderAdvancedCreate(**json_data)
        return True, reader.model_dump()  # Fixed: using model_dump() instead of dict()
    except Exception as e:
        return False, str(e)

# Database Operations Class
class LibraryCRUD:
    # BOOKS CRUD Operations
    @staticmethod
    def get_all_books() -> List[Dict]:
        """Get all books from database"""
        query = "SELECT * FROM books"
        return db_manager.execute_query(query)
    
    @staticmethod
    def get_book_by_id(book_id: int) -> Dict:
        """Get a specific book by ID"""
        query = "SELECT * FROM books WHERE book_id = ?"
        results = db_manager.execute_query(query, (book_id,))
        return results[0] if results else None
    
    @staticmethod
    def create_book(book_data: BookCreate) -> int:
        """Create a new book"""
        query = """
            INSERT INTO books (title, author, genre, stock)
            VALUES (?, ?, ?, ?)
        """
        return db_manager.execute_update(
            query, 
            (book_data.title, book_data.author, book_data.genre, book_data.stock)
        )
    
    @staticmethod
    def update_book(book_id: int, book_data: BookUpdate) -> bool:
        """Update a book"""
        # Build dynamic update query
        updates = []
        params = []
        
        if book_data.title is not None:
            updates.append("title = ?")
            params.append(book_data.title)
        if book_data.author is not None:
            updates.append("author = ?")
            params.append(book_data.author)
        if book_data.genre is not None:
            updates.append("genre = ?")
            params.append(book_data.genre)
        if book_data.stock is not None:
            updates.append("stock = ?")
            params.append(book_data.stock)
        
        if not updates:
            return True  # No updates to make
        
        query = f"UPDATE books SET {', '.join(updates)} WHERE book_id = ?"
        params.append(book_id)
        
        db_manager.execute_update(query, tuple(params))
        return True
    
    @staticmethod
    def delete_book(book_id: int) -> bool:
        """Delete a book"""
        query = "DELETE FROM books WHERE book_id = ?"
        db_manager.execute_update(query, (book_id,))
        return True
    
    # STAFF CRUD Operations
    @staticmethod
    def get_all_staff() -> List[Dict]:
        """Get all staff members"""
        query = "SELECT * FROM staff"
        return db_manager.execute_query(query)
    
    @staticmethod
    def get_staff_by_id(staff_id: int) -> Dict:
        """Get a specific staff member by ID"""
        query = "SELECT * FROM staff WHERE staff_id = ?"
        results = db_manager.execute_query(query, (staff_id,))
        return results[0] if results else None
    
    @staticmethod
    def create_staff(staff_data: StaffCreate) -> int:
        """Create a new staff member"""
        query = """
            INSERT INTO staff (name, role, contact)
            VALUES (?, ?, ?)
        """
        return db_manager.execute_update(
            query,
            (staff_data.name, staff_data.role, staff_data.contact)
        )
    
    @staticmethod
    def update_staff(staff_id: int, staff_data: StaffUpdate) -> bool:
        """Update a staff member"""
        # Build dynamic update query
        updates = []
        params = []
        
        if staff_data.name is not None:
            updates.append("name = ?")
            params.append(staff_data.name)
        if staff_data.role is not None:
            updates.append("role = ?")
            params.append(staff_data.role)
        if staff_data.contact is not None:
            updates.append("contact = ?")
            params.append(staff_data.contact)
        
        if not updates:
            return True  # No updates to make
        
        query = f"UPDATE staff SET {', '.join(updates)} WHERE staff_id = ?"
        params.append(staff_id)
        
        db_manager.execute_update(query, tuple(params))
        return True
    
    @staticmethod
    def delete_staff(staff_id: int) -> bool:
        """Delete a staff member"""
        query = "DELETE FROM staff WHERE staff_id = ?"
        db_manager.execute_update(query, (staff_id,))
        return True
    
    # READERS CRUD Operations
    @staticmethod
    def get_all_readers() -> List[Dict]:
        """Get all readers"""
        query = "SELECT * FROM readers"
        return db_manager.execute_query(query)
    
    @staticmethod
    def get_reader_by_id(reader_id: int) -> Dict:
        """Get a specific reader by ID"""
        query = "SELECT * FROM readers WHERE reader_id = ?"
        results = db_manager.execute_query(query, (reader_id,))
        return results[0] if results else None
    
    @staticmethod
    def create_reader(reader_data: ReaderCreate) -> int:
        """Create a new reader"""
        query = """
            INSERT INTO readers (name, contact, borrowed_books)
            VALUES (?, ?, ?)
        """
        return db_manager.execute_update(
            query,
            (reader_data.name, reader_data.contact, '[]')
        )
    
    @staticmethod
    def update_reader(reader_id: int, reader_data: ReaderUpdate) -> bool:
        """Update a reader"""
        # Build dynamic update query
        updates = []
        params = []
        
        if reader_data.name is not None:
            updates.append("name = ?")
            params.append(reader_data.name)
        if reader_data.contact is not None:
            updates.append("contact = ?")
            params.append(reader_data.contact)
        
        if not updates:
            return True  # No updates to make
        
        query = f"UPDATE readers SET {', '.join(updates)} WHERE reader_id = ?"
        params.append(reader_id)
        
        db_manager.execute_update(query, tuple(params))
        return True
    
    @staticmethod
    def delete_reader(reader_id: int) -> bool:
        """Delete a reader"""
        query = "DELETE FROM readers WHERE reader_id = ?"
        db_manager.execute_update(query, (reader_id,))
        return True

# Initialize CRUD operations
crud = LibraryCRUD()

# FastAPI Application
app = FastAPI(
    title="Library Management System API",
    description="Complete library management system with SQLite database integration and advanced JSON handling",
    version="3.0.0"
)

# Root endpoint
@app.get("/")
def root():
    return {
        "message": "Library Management System API",
        "version": "3.0.0",
        "database": "SQLite",
        "timestamp": datetime.now().isoformat()
    }

# Health check endpoint
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "database": "connected",
        "timestamp": datetime.now().isoformat()
    }

# BOOKS CRUD ENDPOINTS
@app.get("/books", response_model=List[BookResponse])
def get_books():
    """Get all books"""
    books = crud.get_all_books()
    return books

@app.get("/books/{book_id}", response_model=BookResponse)
def get_book(book_id: int):
    """Get a specific book by ID"""
    book = crud.get_book_by_id(book_id)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with ID {book_id} not found"
        )
    return book

@app.post("/books", response_model=Dict)
def create_book(book_data: BookCreate):
    """Create a new book"""
    book_id = crud.create_book(book_data)
    new_book = crud.get_book_by_id(book_id)
    return {
        "message": "Book created successfully",
        "book": new_book
    }

@app.put("/books/{book_id}", response_model=Dict)
def update_book(book_id: int, book_data: BookUpdate):
    """Update a book"""
    existing_book = crud.get_book_by_id(book_id)
    if not existing_book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with ID {book_id} not found"
        )
    
    crud.update_book(book_id, book_data)
    updated_book = crud.get_book_by_id(book_id)
    return {
        "message": "Book updated successfully",
        "book": updated_book
    }

@app.delete("/books/{book_id}")
def delete_book(book_id: int):
    """Delete a book"""
    existing_book = crud.get_book_by_id(book_id)
    if not existing_book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with ID {book_id} not found"
        )
    
    crud.delete_book(book_id)
    return {"message": f"Book with ID {book_id} deleted successfully"}

# STAFF CRUD ENDPOINTS
@app.get("/staff", response_model=List[StaffResponse])
def get_staff():
    """Get all staff members"""
    staff = crud.get_all_staff()
    return staff

@app.get("/staff/{staff_id}", response_model=StaffResponse)
def get_staff_member(staff_id: int):
    """Get a specific staff member by ID"""
    staff = crud.get_staff_by_id(staff_id)
    if not staff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Staff member with ID {staff_id} not found"
        )
    return staff

@app.post("/staff", response_model=Dict)
def create_staff(staff_data: StaffCreate):
    """Create a new staff member"""
    staff_id = crud.create_staff(staff_data)
    new_staff = crud.get_staff_by_id(staff_id)
    return {
        "message": "Staff member created successfully",
        "staff": new_staff
    }

@app.put("/staff/{staff_id}", response_model=Dict)
def update_staff(staff_id: int, staff_data: StaffUpdate):
    """Update a staff member"""
    existing_staff = crud.get_staff_by_id(staff_id)
    if not existing_staff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Staff member with ID {staff_id} not found"
        )
    
    crud.update_staff(staff_id, staff_data)
    updated_staff = crud.get_staff_by_id(staff_id)
    return {
        "message": "Staff member updated successfully",
        "staff": updated_staff
    }

@app.delete("/staff/{staff_id}")
def delete_staff(staff_id: int):
    """Delete a staff member"""
    existing_staff = crud.get_staff_by_id(staff_id)
    if not existing_staff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Staff member with ID {staff_id} not found"
        )
    
    crud.delete_staff(staff_id)
    return {"message": f"Staff member with ID {staff_id} deleted successfully"}

# READERS CRUD ENDPOINTS
@app.get("/readers", response_model=List[ReaderResponse])
def get_readers():
    """Get all readers"""
    readers = crud.get_all_readers()
    # Parse borrowed_books from JSON string to list
    for reader in readers:
        if isinstance(reader.get('borrowed_books'), str):
            try:
                reader['borrowed_books'] = json.loads(reader['borrowed_books'])
            except:
                reader['borrowed_books'] = []
    return readers

@app.get("/readers/{reader_id}", response_model=ReaderResponse)
def get_reader(reader_id: int):
    """Get a specific reader by ID"""
    reader = crud.get_reader_by_id(reader_id)
    if not reader:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reader with ID {reader_id} not found"
        )
    
    # Parse borrowed_books
    if isinstance(reader.get('borrowed_books'), str):
        try:
            reader['borrowed_books'] = json.loads(reader['borrowed_books'])
        except:
            reader['borrowed_books'] = []
    
    return reader

@app.post("/readers", response_model=Dict)
def create_reader(reader_data: ReaderCreate):
    """Create a new reader"""
    reader_id = crud.create_reader(reader_data)
    new_reader = crud.get_reader_by_id(reader_id)
    
    # Parse borrowed_books
    if isinstance(new_reader.get('borrowed_books'), str):
        new_reader['borrowed_books'] = json.loads(new_reader['borrowed_books'])
    
    return {
        "message": "Reader created successfully",
        "reader": new_reader
    }

@app.put("/readers/{reader_id}", response_model=Dict)
def update_reader(reader_id: int, reader_data: ReaderUpdate):
    """Update a reader"""
    existing_reader = crud.get_reader_by_id(reader_id)
    if not existing_reader:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reader with ID {reader_id} not found"
        )
    
    crud.update_reader(reader_id, reader_data)
    updated_reader = crud.get_reader_by_id(reader_id)
    
    # Parse borrowed_books
    if isinstance(updated_reader.get('borrowed_books'), str):
        updated_reader['borrowed_books'] = json.loads(updated_reader['borrowed_books'])
    
    return {
        "message": "Reader updated successfully",
        "reader": updated_reader
    }

@app.delete("/readers/{reader_id}")
def delete_reader(reader_id: int):
    """Delete a reader"""
    existing_reader = crud.get_reader_by_id(reader_id)
    if not existing_reader:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reader with ID {reader_id} not found"
        )
    
    crud.delete_reader(reader_id)
    return {"message": f"Reader with ID {reader_id} deleted successfully"}

# ADVANCED JSON HANDLING ENDPOINTS
@app.post("/books/advanced", response_model=BookAdvancedResponse)
def create_book_advanced(book_data: BookAdvancedCreate):
    """Create a new book with nested JSON structure"""
    # Convert advanced format to basic format for database
    basic_book = BookCreate(
        title=book_data.title,
        author=book_data.author,
        genre=book_data.details.genre,
        stock=book_data.details.stock
    )
    
    book_id = crud.create_book(basic_book)
    new_book = crud.get_book_by_id(book_id)
    
    # Return in advanced nested format
    return BookAdvancedResponse(
        book_id=new_book['book_id'],
        title=new_book['title'],
        author=new_book['author'],
        details=BookDetails(
            genre=new_book['genre'],
            stock=new_book['stock']
        )
    )

@app.get("/books/advanced/{book_id}", response_model=BookAdvancedResponse)
def get_book_advanced(book_id: int):
    """Get a book with nested JSON response"""
    book = crud.get_book_by_id(book_id)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with ID {book_id} not found"
        )
    
    return BookAdvancedResponse(
        book_id=book['book_id'],
        title=book['title'],
        author=book['author'],
        details=BookDetails(
            genre=book['genre'],
            stock=book['stock']
        )
    )

@app.post("/readers/advanced", response_model=ReaderAdvancedResponse)
def create_reader_advanced(reader_data: ReaderAdvancedCreate):
    """Create a new reader with nested JSON structure"""
    # Convert advanced format to basic format for database
    basic_reader = ReaderCreate(
        name=reader_data.name,
        contact=reader_data.details.contact
    )
    
    reader_id = crud.create_reader(basic_reader)
    new_reader = crud.get_reader_by_id(reader_id)
    
    # Parse borrowed_books
    borrowed_books = []
    if isinstance(new_reader.get('borrowed_books'), str):
        try:
            borrowed_books = json.loads(new_reader['borrowed_books'])
        except:
            borrowed_books = []
    
    # Return in advanced nested format
    return ReaderAdvancedResponse(
        reader_id=new_reader['reader_id'],
        name=new_reader['name'],
        details=ReaderDetails(
            contact=new_reader['contact'],
            borrowed_books=borrowed_books
        )
    )

@app.get("/readers/advanced/{reader_id}", response_model=ReaderAdvancedResponse)
def get_reader_advanced(reader_id: int):
    """Get a reader with nested JSON response"""
    reader = crud.get_reader_by_id(reader_id)
    if not reader:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reader with ID {reader_id} not found"
        )
    
    # Parse borrowed_books
    borrowed_books = []
    if isinstance(reader.get('borrowed_books'), str):
        try:
            borrowed_books = json.loads(reader['borrowed_books'])
        except:
            borrowed_books = []
    
    return ReaderAdvancedResponse(
        reader_id=reader['reader_id'],
        name=reader['name'],
        details=ReaderDetails(
            contact=reader['contact'],
            borrowed_books=borrowed_books
        )
    )

# JSON VALIDATION ENDPOINTS
@app.post("/validate/book")
def validate_book_json_endpoint(payload: Dict):
    """Validate book JSON payload"""
    is_valid, result = validate_book_json(payload)
    if is_valid:
        return {
            "valid": True,
            "message": "JSON payload is valid",
            "data": result
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid JSON payload: {result}"
        )

@app.post("/validate/reader")
def validate_reader_json_endpoint(payload: Dict):
    """Validate reader JSON payload"""
    is_valid, result = validate_reader_json(payload)
    if is_valid:
        return {
            "valid": True,
            "message": "JSON payload is valid",
            "data": result
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid JSON payload: {result}"
        )

# Database initialization endpoint
@app.post("/init-db")
def initialize_database():
    """Initialize the database (creates tables if they don't exist)"""
    db_manager.init_database()
    return {"message": "Database initialized successfully"}

# Database cleanup endpoint (for testing)
@app.post("/clear-db")
def clear_database():
    """Clear all data from database (for testing purposes)"""
    db_manager.clear_database()
    return {"message": "Database cleared successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
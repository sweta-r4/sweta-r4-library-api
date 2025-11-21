from pydantic import BaseModel, validator
from typing import Dict, List, Optional
import json
from datetime import datetime

# Complex JSON Models for Nested Structures
class BookDetails(BaseModel):
    genre: Optional[str] = None
    stock: Optional[int] = 1
    isbn: Optional[str] = None
    published_year: Optional[int] = None
    available: Optional[bool] = True

class BookCreateAdvanced(BaseModel):
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

class BookResponseAdvanced(BaseModel):
    book_id: int
    title: str
    author: str
    details: BookDetails

class ReaderDetails(BaseModel):
    contact: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    membership_type: Optional[str] = "Standard"
    join_date: Optional[str] = None
    books_borrowed: Optional[List[int]] = []

class ReaderCreateAdvanced(BaseModel):
    name: str
    membership_id: str
    details: ReaderDetails

class ReaderResponseAdvanced(BaseModel):
    reader_id: int
    name: str
    membership_id: str
    details: ReaderDetails

# JSON Validation Functions
def validate_book_json(json_data: Dict) -> tuple:
    """Validate book JSON payload"""
    try:
        book = BookCreateAdvanced(**json_data)
        return True, book.dict()
    except Exception as e:
        return False, str(e)

def validate_reader_json(json_data: Dict) -> tuple:
    """Validate reader JSON payload"""
    try:
        reader = ReaderCreateAdvanced(**json_data)
        return True, reader.dict()
    except Exception as e:
        return False, str(e)

# JSON Response Formatters
def format_book_response(book_data: Dict) -> Dict:
    """Format book data for nested JSON response"""
    details = BookDetails(
        genre=book_data.get('genre'),
        stock=book_data.get('stock', 1),
        isbn=book_data.get('isbn'),
        published_year=book_data.get('published_year'),
        available=book_data.get('available', True)
    )
    
    return BookResponseAdvanced(
        book_id=book_data['book_id'],
        title=book_data['title'],
        author=book_data['author'],
        details=details
    ).dict()

def format_reader_response(reader_data: Dict) -> Dict:
    """Format reader data for nested JSON response"""
    # Parse borrowed_books from string to list if needed
    borrowed_books = reader_data.get('borrowed_books', '[]')
    if isinstance(borrowed_books, str):
        try:
            borrowed_books = json.loads(borrowed_books)
        except:
            borrowed_books = []
    
    details = ReaderDetails(
        contact=reader_data.get('contact'),
        email=reader_data.get('email'),
        phone=reader_data.get('phone'),
        membership_type=reader_data.get('membership_type', 'Standard'),
        join_date=reader_data.get('join_date'),
        books_borrowed=borrowed_books
    )
    
    return ReaderResponseAdvanced(
        reader_id=reader_data['reader_id'],
        name=reader_data['name'],
        membership_id=reader_data['membership_id'],
        details=details
    ).dict()
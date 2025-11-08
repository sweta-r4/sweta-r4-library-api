from fastapi import FastAPI, Request, HTTPException, status
import logging
import os
import time
from typing import List, Dict, Optional

# Ensure logs directory exists in the ROOT directory (not inside app/)
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)  # Go up one level to the root
logs_dir = os.path.join(root_dir, "logs")
os.makedirs(logs_dir, exist_ok=True)

# Clear any existing logging configuration
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

# Setup logging to file in the ROOT logs directory
log_file_path = os.path.join(logs_dir, "app.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    filename=log_file_path,
    filemode="a"  # Append mode
)

# Also add console handler to see logs in terminal
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)
logging.getLogger().addHandler(console_handler)

# MANAGER CLASSES

class BaseManager:
    def __init__(self, file_name: str):
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_dir = os.path.join(self.current_dir, "data")
        self.file_path = os.path.join(self.data_dir, file_name)
        
        # Ensure data directory exists
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Ensure file exists
        if not os.path.exists(self.file_path):
            open(self.file_path, 'w').close()

class BookManager(BaseManager):
    def __init__(self):
        super().__init__("books.txt")
        self.entity_name = "book"

    def get_all_books(self) -> List[Dict]:
        """Get all books from the file"""
        try:
            books = []
            with open(self.file_path, 'r') as file:
                for line_num, line in enumerate(file, 1):
                    if line.strip():
                        parts = line.strip().split(', ')
                        if len(parts) >= 2:
                            books.append({
                                "id": line_num,
                                "title": parts[0],
                                "author": parts[1] if len(parts) > 1 else "Unknown"
                            })
            logging.info(f"Retrieved {len(books)} books")
            return books
        except Exception as e:
            logging.error(f"Error reading books file: {str(e)}")
            return []

    def get_book_by_id(self, book_id: int) -> Optional[Dict]:
        """Get a specific book by ID"""
        books = self.get_all_books()
        for book in books:
            if book["id"] == book_id:
                return book
        return None

    def add_book(self, title: str, author: str) -> Dict:
        """Add a new book to the file"""
        try:
            with open(self.file_path, 'a') as file:
                file.write(f"{title}, {author}\n")
            
            # Get the new book ID
            books = self.get_all_books()
            new_book = books[-1] if books else None
            
            logging.info(f"Added new book: {title} by {author}")
            return new_book
        except Exception as e:
            logging.error(f"Error adding book: {str(e)}")
            raise e

    def update_book(self, book_id: int, title: str, author: str) -> Optional[Dict]:
        """Update a book by its ID"""
        try:
            books = self.get_all_books()
            updated = False
            
            for book in books:
                if book["id"] == book_id:
                    book["title"] = title
                    book["author"] = author
                    updated = True
                    break
            
            if updated:
                # Rewrite the entire file
                with open(self.file_path, 'w') as file:
                    for book in books:
                        file.write(f"{book['title']}, {book['author']}\n")
                
                logging.info(f"Updated book ID {book_id}: {title} by {author}")
                return self.get_book_by_id(book_id)
            else:
                logging.warning(f"Book with ID {book_id} not found for update")
                return None
                
        except Exception as e:
            logging.error(f"Error updating book: {str(e)}")
            raise e

    def delete_book(self, book_id: int) -> bool:
        """Delete a book by its ID"""
        try:
            books = self.get_all_books()
            original_count = len(books)
            
            # Filter out the book to delete
            books = [book for book in books if book["id"] != book_id]
            
            if len(books) < original_count:
                # Rewrite the file without the deleted book
                with open(self.file_path, 'w') as file:
                    for book in books:
                        file.write(f"{book['title']}, {book['author']}\n")
                
                logging.info(f"Deleted book with ID {book_id}")
                return True
            else:
                logging.warning(f"Book with ID {book_id} not found for deletion")
                return False
                
        except Exception as e:
            logging.error(f"Error deleting book: {str(e)}")
            raise e

class ReaderManager(BaseManager):
    def __init__(self):
        super().__init__("readers.txt")
        self.entity_name = "reader"

    def get_all_readers(self) -> List[Dict]:
        """Get all readers from the file"""
        try:
            readers = []
            if os.path.exists(self.file_path):
                with open(self.file_path, 'r') as file:
                    for line_num, line in enumerate(file, 1):
                        if line.strip():
                            parts = line.strip().split(', ')
                            if len(parts) >= 2:
                                readers.append({
                                    "id": line_num,
                                    "name": parts[0],
                                    "membership_id": parts[1]
                                })
            logging.info(f"Retrieved {len(readers)} readers")
            return readers
        except Exception as e:
            logging.error(f"Error reading readers file: {str(e)}")
            return []

    def get_reader_by_id(self, reader_id: int) -> Optional[Dict]:
        """Get a specific reader by ID"""
        readers = self.get_all_readers()
        for reader in readers:
            if reader["id"] == reader_id:
                return reader
        return None

    def add_reader(self, name: str, membership_id: str) -> Dict:
        """Add a new reader to the file"""
        try:
            with open(self.file_path, 'a') as file:
                file.write(f"{name}, {membership_id}\n")
            
            readers = self.get_all_readers()
            new_reader = readers[-1] if readers else None
            
            logging.info(f"Added new reader: {name} with membership ID {membership_id}")
            return new_reader
        except Exception as e:
            logging.error(f"Error adding reader: {str(e)}")
            raise e

    def update_reader(self, reader_id: int, name: str, membership_id: str) -> Optional[Dict]:
        """Update a reader by ID"""
        try:
            readers = self.get_all_readers()
            updated = False
            
            for reader in readers:
                if reader["id"] == reader_id:
                    reader["name"] = name
                    reader["membership_id"] = membership_id
                    updated = True
                    break
            
            if updated:
                with open(self.file_path, 'w') as file:
                    for reader in readers:
                        file.write(f"{reader['name']}, {reader['membership_id']}\n")
                
                logging.info(f"Updated reader ID {reader_id}: {name} with membership ID {membership_id}")
                return self.get_reader_by_id(reader_id)
            else:
                logging.warning(f"Reader with ID {reader_id} not found for update")
                return None
                
        except Exception as e:
            logging.error(f"Error updating reader: {str(e)}")
            raise e

    def delete_reader(self, reader_id: int) -> bool:
        """Delete a reader by ID"""
        try:
            readers = self.get_all_readers()
            original_count = len(readers)
            
            readers = [reader for reader in readers if reader["id"] != reader_id]
            
            if len(readers) < original_count:
                with open(self.file_path, 'w') as file:
                    for reader in readers:
                        file.write(f"{reader['name']}, {reader['membership_id']}\n")
                
                logging.info(f"Deleted reader with ID {reader_id}")
                return True
            else:
                logging.warning(f"Reader with ID {reader_id} not found for deletion")
                return False
                
        except Exception as e:
            logging.error(f"Error deleting reader: {str(e)}")
            raise e

class StaffManager(BaseManager):
    def __init__(self):
        super().__init__("staff.txt")
        self.entity_name = "staff"

    def get_all_staff(self) -> List[Dict]:
        """Get all staff members from the file"""
        try:
            staff_members = []
            if os.path.exists(self.file_path):
                with open(self.file_path, 'r') as file:
                    for line_num, line in enumerate(file, 1):
                        if line.strip():
                            parts = line.strip().split(', ')
                            if len(parts) >= 2:
                                staff_members.append({
                                    "id": line_num,
                                    "name": parts[0],
                                    "position": parts[1]
                                })
            logging.info(f"Retrieved {len(staff_members)} staff members")
            return staff_members
        except Exception as e:
            logging.error(f"Error reading staff file: {str(e)}")
            return []

    def get_staff_by_id(self, staff_id: int) -> Optional[Dict]:
        """Get a specific staff member by ID"""
        staff_members = self.get_all_staff()
        for staff in staff_members:
            if staff["id"] == staff_id:
                return staff
        return None

    def add_staff(self, name: str, position: str) -> Dict:
        """Add a new staff member to the file"""
        try:
            with open(self.file_path, 'a') as file:
                file.write(f"{name}, {position}\n")
            
            staff_members = self.get_all_staff()
            new_staff = staff_members[-1] if staff_members else None
            
            logging.info(f"Added new staff member: {name} as {position}")
            return new_staff
        except Exception as e:
            logging.error(f"Error adding staff: {str(e)}")
            raise e

    def update_staff(self, staff_id: int, name: str, position: str) -> Optional[Dict]:
        """Update a staff member by ID"""
        try:
            staff_members = self.get_all_staff()
            updated = False
            
            for staff in staff_members:
                if staff["id"] == staff_id:
                    staff["name"] = name
                    staff["position"] = position
                    updated = True
                    break
            
            if updated:
                with open(self.file_path, 'w') as file:
                    for staff in staff_members:
                        file.write(f"{staff['name']}, {staff['position']}\n")
                
                logging.info(f"Updated staff ID {staff_id}: {name} as {position}")
                return self.get_staff_by_id(staff_id)
            else:
                logging.warning(f"Staff with ID {staff_id} not found for update")
                return None
                
        except Exception as e:
            logging.error(f"Error updating staff: {str(e)}")
            raise e

    def delete_staff(self, staff_id: int) -> bool:
        """Delete a staff member by ID"""
        try:
            staff_members = self.get_all_staff()
            original_count = len(staff_members)
            
            staff_members = [staff for staff in staff_members if staff["id"] != staff_id]
            
            if len(staff_members) < original_count:
                with open(self.file_path, 'w') as file:
                    for staff in staff_members:
                        file.write(f"{staff['name']}, {staff['position']}\n")
                
                logging.info(f"Deleted staff with ID {staff_id}")
                return True
            else:
                logging.warning(f"Staff with ID {staff_id} not found for deletion")
                return False
                
        except Exception as e:
            logging.error(f"Error deleting staff: {str(e)}")
            raise e

# FASTAPI APPLICATION

app = FastAPI(title="Library Management System", version="1.0.0")

# Initialize managers
book_manager = BookManager()
reader_manager = ReaderManager()
staff_manager = StaffManager()

# Request counter and error counter
request_counter: Dict[str, int] = {}
error_counter = 0

# Middleware for enhanced logging and monitoring
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Log incoming request
    logging.info(f"Request: {request.method} {request.url.path}")
    
    # Count requests by endpoint
    endpoint = request.url.path
    request_counter[endpoint] = request_counter.get(endpoint, 0) + 1
    
    try:
        response = await call_next(request)
        process_time = (time.time() - start_time) * 1000
        
        # Log response
        logging.info(f"Response: {response.status_code} - Time: {process_time:.2f}ms")
        
        return response
        
    except Exception as e:
        global error_counter
        error_counter += 1
        process_time = (time.time() - start_time) * 1000
        logging.error(f"Error: {str(e)} - Time: {process_time:.2f}ms")
        raise e

@app.get("/")
def home():
    """Root endpoint."""
    return {"message": "Library Management System"}

@app.get("/items")
def get_items():
    """Get all books from the library (legacy endpoint)."""
    books = book_manager.get_all_books()
    return [f"{book['title']} by {book['author']}" for book in books]

@app.get("/health")
def health_check():
    """Health check endpoint with monitoring stats."""
    return {
        "status": "ok",
        "request_counts": request_counter,
        "total_errors": error_counter
    }

# BOOKS CRUD ENDPOINTS

@app.get("/books")
def get_all_books():
    """Get all books with details."""
    return book_manager.get_all_books()

@app.post("/books")
def add_book(title: str, author: str):
    """Add a new book."""
    if not title or not author:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Title and author are required"
        )
    
    new_book = book_manager.add_book(title, author)
    return {"message": "Book added successfully", "book": new_book}

@app.put("/books/{book_id}")
def update_book(book_id: int, title: str, author: str):
    """Update a book by ID."""
    if not title or not author:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Title and author are required"
        )
    
    updated_book = book_manager.update_book(book_id, title, author)
    if updated_book:
        return {"message": "Book updated successfully", "book": updated_book}
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with ID {book_id} not found"
        )

@app.delete("/books/{book_id}")
def delete_book(book_id: int):
    """Delete a book by ID."""
    success = book_manager.delete_book(book_id)
    if success:
        return {"message": f"Book with ID {book_id} deleted successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with ID {book_id} not found"
        )

# READERS CRUD ENDPOINTS

@app.get("/readers")
def get_all_readers():
    """Get all readers."""
    return reader_manager.get_all_readers()

@app.post("/readers")
def add_reader(name: str, membership_id: str):
    """Add a new reader."""
    if not name or not membership_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Name and membership ID are required"
        )
    
    new_reader = reader_manager.add_reader(name, membership_id)
    return {"message": "Reader added successfully", "reader": new_reader}

@app.put("/readers/{reader_id}")
def update_reader(reader_id: int, name: str, membership_id: str):
    """Update a reader by ID."""
    if not name or not membership_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Name and membership ID are required"
        )
    
    updated_reader = reader_manager.update_reader(reader_id, name, membership_id)
    if updated_reader:
        return {"message": "Reader updated successfully", "reader": updated_reader}
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reader with ID {reader_id} not found"
        )

@app.delete("/readers/{reader_id}")
def delete_reader(reader_id: int):
    """Delete a reader by ID."""
    success = reader_manager.delete_reader(reader_id)
    if success:
        return {"message": f"Reader with ID {reader_id} deleted successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reader with ID {reader_id} not found"
        )

# STAFF CRUD ENDPOINTS

@app.get("/staff")
def get_all_staff():
    """Get all staff members."""
    return staff_manager.get_all_staff()

@app.post("/staff")
def add_staff(name: str, position: str):
    """Add a new staff member."""
    if not name or not position:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Name and position are required"
        )
    
    new_staff = staff_manager.add_staff(name, position)
    return {"message": "Staff member added successfully", "staff": new_staff}

@app.put("/staff/{staff_id}")
def update_staff(staff_id: int, name: str, position: str):
    """Update a staff member by ID."""
    if not name or not position:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Name and position are required"
        )
    
    updated_staff = staff_manager.update_staff(staff_id, name, position)
    if updated_staff:
        return {"message": "Staff member updated successfully", "staff": updated_staff}
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Staff member with ID {staff_id} not found"
        )

@app.delete("/staff/{staff_id}")
def delete_staff(staff_id: int):
    """Delete a staff member by ID."""
    success = staff_manager.delete_staff(staff_id)
    if success:
        return {"message": f"Staff member with ID {staff_id} deleted successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Staff member with ID {staff_id} not found"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
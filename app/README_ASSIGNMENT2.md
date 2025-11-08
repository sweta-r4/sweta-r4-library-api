# Assignment 2 Submission - Library Management System

## OOP Refactoring
- BaseManager class for common functionality
- BookManager, ReaderManager, StaffManager classes
- Encapsulated CRUD operations

## API Endpoints Implemented
### Books
- `GET /books` - Retrieve all books
- `POST /books` - Add new book
- `PUT /books/{id}` - Update book
- `DELETE /books/{id}` - Delete book

### Readers
- `GET /readers` - Retrieve all readers
- `POST /readers` - Add new reader
- `PUT /readers/{id}` - Update reader
- `DELETE /readers/{id}` - Delete reader

### Staff
- `GET /staff` - Retrieve all staff
- `POST /staff` - Add new staff
- `PUT /staff/{id}` - Update staff
- `DELETE /staff/{id}` - Delete staff

### Monitoring
- `GET /health` - Health check with statistics

## Enhanced Features
- Request/response logging
- Error tracking
- File-based persistence
- Input validation

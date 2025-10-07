from fastapi import FastAPI, Request
import logging
import os

# Ensure logs directory exists
os.makedirs("logs", exist_ok=True)

# Setup logging to file
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    filename="logs/app.log",  # This will save logs to file
    filemode="w"  # Overwrite old log file
)

app = FastAPI()

# Middleware for automatic logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logging.info(f"Request: {request.method} {request.url.path}")
    response = await call_next(request)
    logging.info(f"Response: {response.status_code}")
    return response

@app.get("/")
def home():
    return {"message": "Library Management System"}

@app.get("/items")
def get_items():
    try:
        # Read from data/books.txt
        file = open("../data/books.txt", "r")
        content = file.read()
        file.close()
        
    except FileNotFoundError:
        return ["The Great Gatsby", "To Kill a Mockingbird", "1984"]
        
    except Exception as e:
        return ["Error loading books"]
    
    # Process the book data
    books_list = []
    for line in content.splitlines():
        book = line.strip()
        if book:
            books_list.append(book)
    
    return books_list

@app.get("/health")
def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

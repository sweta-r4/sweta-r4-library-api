
import json
import os

def convert_books_to_json():
    """Convert books.txt to books.json"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(current_dir, "data")
    
    txt_file = os.path.join(data_dir, "books.txt")
    json_file = os.path.join(data_dir, "books.json")
    
    books = []
    
    # Read from text file
    if os.path.exists(txt_file):
        with open(txt_file, 'r') as f:
            for line_num, line in enumerate(f, 1):
                if line.strip():
                    parts = line.strip().split(', ')
                    if len(parts) >= 2:
                        books.append({
                            "id": line_num,
                            "title": parts[0],
                            "author": parts[1],
                            "isbn": "",
                            "published_year": None,
                            "genre": "",
                            "available": True
                        })
    
    # Write to JSON file
    with open(json_file, 'w') as f:
        json.dump({"books": books}, f, indent=2)
    
    print(f"Converted {len(books)} books to JSON")

def convert_readers_to_json():
    """Convert readers.txt to readers.json"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(current_dir, "data")
    
    txt_file = os.path.join(data_dir, "readers.txt")
    json_file = os.path.join(data_dir, "readers.json")
    
    readers = []
    
    # Read from text file
    if os.path.exists(txt_file):
        with open(txt_file, 'r') as f:
            for line_num, line in enumerate(f, 1):
                if line.strip():
                    parts = line.strip().split(', ')
                    if len(parts) >= 2:
                        readers.append({
                            "id": line_num,
                            "name": parts[0],
                            "membership_id": parts[1],
                            "email": "",
                            "phone": "",
                            "membership_type": "Standard",
                            "join_date": "2024-01-01",
                            "books_borrowed": []
                        })
    
    # Write to JSON file
    with open(json_file, 'w') as f:
        json.dump({"readers": readers}, f, indent=2)
    
    print(f"Converted {len(readers)} readers to JSON")

def convert_staff_to_json():
    """Convert staff.txt to staff.json"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(current_dir, "data")
    
    txt_file = os.path.join(data_dir, "staff.txt")
    json_file = os.path.join(data_dir, "staff.json")
    
    staff_members = []
    
    # Read from text file
    if os.path.exists(txt_file):
        with open(txt_file, 'r') as f:
            for line_num, line in enumerate(f, 1):
                if line.strip():
                    parts = line.strip().split(', ')
                    if len(parts) >= 2:
                        staff_members.append({
                            "id": line_num,
                            "name": parts[0],
                            "position": parts[1],
                            "email": "",
                            "phone": "",
                            "department": "",
                            "salary": 0,
                            "hire_date": "2024-01-01",
                            "is_active": True
                        })
    
    # Write to JSON file
    with open(json_file, 'w') as f:
        json.dump({"staff": staff_members}, f, indent=2)
    
    print(f"Converted {len(staff_members)} staff members to JSON")

if __name__ == "__main__":
    convert_books_to_json()
    convert_readers_to_json()
    convert_staff_to_json()
    print("All files converted to JSON format!")

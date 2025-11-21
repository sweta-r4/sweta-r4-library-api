# app/database_to_json.py
import json
import os
import sqlite3
from datetime import datetime

def convert_database_to_json():
    """Convert current SQLite database to JSON files"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(current_dir, "data")
    db_path = os.path.join(data_dir, "library.db")
    
    print(f" Converting database: {db_path}")
    
    if not os.path.exists(db_path):
        print(" Database file not found!")
        return
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    print(f" Found tables: {tables}")
    
    # Convert each table to JSON
    for table in tables:
        try:
            cursor.execute(f"SELECT * FROM {table}")
            rows = cursor.fetchall()
            
            # Convert to list of dictionaries
            data = []
            for row in rows:
                row_dict = dict(row)
                # Handle JSON strings
                if 'borrowed_books' in row_dict and isinstance(row_dict['borrowed_books'], str):
                    try:
                        row_dict['borrowed_books'] = json.loads(row_dict['borrowed_books'])
                    except:
                        row_dict['borrowed_books'] = []
                data.append(row_dict)
            
            # Save to JSON file
            json_path = os.path.join(data_dir, f"{table}.json")
            with open(json_path, 'w') as f:
                json.dump({
                    "table": table,
                    "count": len(data),
                    "exported_at": datetime.now().isoformat(),
                    "data": data
                }, f, indent=2)
            
            print(f" Converted {len(data)} records from '{table}' table")
            
            # Show sample data
            if data:
                print(f"   Sample: {data[0]}")
                
        except Exception as e:
            print(f" Error converting table '{table}': {e}")
    
    conn.close()
    print("\n Database conversion completed!")

def show_current_data():
    """Show current data in database"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(current_dir, "data", "library.db")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("\n CURRENT DATABASE DATA:")
    print("=" * 50)
    
    # Show books
    cursor.execute("SELECT COUNT(*) as count FROM books")
    book_count = cursor.fetchone()[0]
    print(f" Books in database: {book_count}")
    
    cursor.execute("SELECT book_id, title, author, stock FROM books ORDER BY book_id DESC LIMIT 5")
    recent_books = cursor.fetchall()
    print("   Recent books:")
    for book in recent_books:
        print(f"     ID {book[0]}: '{book[1]}' by {book[2]} (Stock: {book[3]})")
    
    # Show staff
    cursor.execute("SELECT COUNT(*) as count FROM staff")
    staff_count = cursor.fetchone()[0]
    print(f" Staff in database: {staff_count}")
    
    # Show readers
    cursor.execute("SELECT COUNT(*) as count FROM readers")
    reader_count = cursor.fetchone()[0]
    print(f" Readers in database: {reader_count}")
    
    conn.close()

if __name__ == "__main__":
    print(" DATABASE TO JSON CONVERTER")
    print("=" * 40)
    
    # Show current data
    show_current_data()
    
    # Convert to JSON
    print("\n" + "=" * 40)
    convert_database_to_json()
    
    # Show generated files
    print("\n GENERATED JSON FILES:")
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(current_dir, "data")
    
    for file in ["books.json", "staff.json", "readers.json"]:
        file_path = os.path.join(data_dir, file)
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            print(f" {file} ({file_size} bytes)")
        else:
            print(f" {file} (Not found)")
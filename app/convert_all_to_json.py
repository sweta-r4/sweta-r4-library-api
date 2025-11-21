# app/convert_all_to_json.py
import json
import os
import sqlite3
from datetime import datetime

def convert_all_tables_to_json():
    """Convert all database tables to JSON files with proper formatting"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(current_dir, "data")
    db_path = os.path.join(data_dir, "library.db")
    
    print(" CONVERTING DATABASE TABLES TO JSON")
    print("=" * 50)
    
    if not os.path.exists(db_path):
        print(" Database file not found!")
        return
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    
    # Get all tables
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    tables = [row[0] for row in cursor.fetchall()]
    
    print(f" Found tables: {tables}")
    print()
    
    for table in tables:
        try:
            # Get table data
            cursor.execute(f"SELECT * FROM {table}")
            rows = cursor.fetchall()
            
            if not rows:
                print(f"  Table '{table}' is empty")
                continue
            
            # Convert to list of dictionaries
            data = []
            for row in rows:
                row_data = dict(row)
                
                # Special handling for each table
                if table == 'readers' and 'borrowed_books' in row_data:
                    # Parse borrowed_books from JSON string to list
                    if isinstance(row_data['borrowed_books'], str):
                        try:
                            row_data['borrowed_books'] = json.loads(row_data['borrowed_books'])
                        except:
                            row_data['borrowed_books'] = []
                
                data.append(row_data)
            
            # Create comprehensive JSON structure
            json_data = {
                "metadata": {
                    "table_name": table,
                    "record_count": len(data),
                    "export_timestamp": datetime.now().isoformat(),
                    "database_source": "library.db"
                },
                "data": data
            }
            
            # Save to JSON file
            json_path = os.path.join(data_dir, f"{table}.json")
            with open(json_path, 'w') as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)
            
            print(f" {table.upper()} TABLE")
            print(f"    File: {table}.json")
            print(f"    Records: {len(data)}")
            
            # Show sample data
            if data:
                sample = data[0]
                if table == 'books':
                    print(f"    Sample: '{sample.get('title', 'N/A')}' by {sample.get('author', 'N/A')}")
                elif table == 'staff':
                    print(f"    Sample: {sample.get('name', 'N/A')} - {sample.get('role', 'N/A')}")
                elif table == 'readers':
                    print(f"    Sample: {sample.get('name', 'N/A')} - Borrowed: {len(sample.get('borrowed_books', []))} books")
            print()
            
        except Exception as e:
            print(f" Error converting table '{table}': {e}")
            print()
    
    conn.close()
    
    # Final summary
    print(" CONVERSION SUMMARY")
    print("=" * 50)
    for table in tables:
        json_path = os.path.join(data_dir, f"{table}.json")
        if os.path.exists(json_path):
            file_size = os.path.getsize(json_path)
            print(f" {table}.json - {file_size} bytes")
        else:
            print(f" {table}.json - Not created")

def show_database_stats():
    """Show current statistics from database"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(current_dir, "data", "library.db")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print(" DATABASE STATISTICS")
    print("=" * 40)
    
    # Books stats
    cursor.execute("SELECT COUNT(*) as count FROM books")
    book_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) as count FROM books WHERE stock > 0")
    available_books = cursor.fetchone()[0]
    print(f" Books: {book_count} total, {available_books} available")
    
    # Staff stats
    cursor.execute("SELECT COUNT(*) as count FROM staff")
    staff_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(DISTINCT role) as roles FROM staff")
    role_count = cursor.fetchone()[0]
    print(f" Staff: {staff_count} members, {role_count} different roles")
    
    # Readers stats
    cursor.execute("SELECT COUNT(*) as count FROM readers")
    reader_count = cursor.fetchone()[0]
    cursor.execute("SELECT SUM(json_array_length(borrowed_books)) as total_borrowed FROM readers")
    total_borrowed = cursor.fetchone()[0] or 0
    print(f" Readers: {reader_count} registered, {total_borrowed} books borrowed")
    
    conn.close()
    print()

if __name__ == "__main__":
    print(" LIBRARY MANAGEMENT SYSTEM - JSON EXPORT")
    print("=" * 60)
    print()
    
    # Show current stats
    show_database_stats()
    
    # Convert to JSON
    convert_all_tables_to_json()
    
    print(" FINAL JSON FILES:")
    print("=" * 40)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(current_dir, "data")
    
    json_files = ["books.json", "staff.json", "readers.json"]
    for file in json_files:
        file_path = os.path.join(data_dir, file)
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            with open(file_path, 'r') as f:
                data = json.load(f)
                record_count = data['metadata']['record_count']
            print(f" {file}: {record_count} records, {file_size} bytes")
        else:
            print(f" {file}: Not found")
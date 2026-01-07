import sqlite3
import pandas as pd

def inspect_db():
    try:
        conn = sqlite3.connect('db.sqlite3')
        cursor = conn.cursor()
        
        print("--- Tables in Database ---")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        for table in tables:
            print(f"- {table[0]}")
            
        print("\n--- Columns in 'recruitment_application' table ---")
        try:
            cursor.execute("PRAGMA table_info(recruitment_application)")
            columns = cursor.fetchall()
            for col in columns:
                print(f"  {col[1]} ({col[2]})")
        except Exception as e:
            print(f"Error reading application table: {e}")

        conn.close()
    except Exception as e:
        print(f"Database error: {e}")

if __name__ == "__main__":
    inspect_db()

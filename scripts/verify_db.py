import sqlite3

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()
try:
    cursor.execute("PRAGMA table_info(recruitment_application)")
    columns = [row[1] for row in cursor.fetchall()]
    print(f"Columns: {columns}")
    with open('db_status.txt', 'w') as f:
        f.write(str(columns))
except Exception as e:
    with open('db_status.txt', 'w') as f:
        f.write(str(e))
conn.close()

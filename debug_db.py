
import sqlite3
import pandas as pd
import os

DB_FILE = 'database.db'

def check():
    if not os.path.exists(DB_FILE):
        print(f"File {DB_FILE} not found")
        return

    conn = sqlite3.connect(DB_FILE)
    try:
        print("--- Tables ---")
        tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table'", conn)
        print(tables)

        for table in tables['name']:
            count = pd.read_sql(f"SELECT count(*) as count FROM {table}", conn).iloc[0,0]
            print(f"Table {table}: {count} rows")
            if count > 0:
                print(f"Sample from {table}:")
                sample = pd.read_sql(f"SELECT * FROM {table} LIMIT 3", conn)
                print(sample)
                print("\n")
                
        print("--- Date distribution in servicios ---")
        dates = pd.read_sql("SELECT fecha FROM servicios", conn)
        dates['fecha_dt'] = pd.to_datetime(dates['fecha'], errors='coerce')
        print(dates['fecha_dt'].dt.strftime('%Y-%m').value_counts())

    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    check()

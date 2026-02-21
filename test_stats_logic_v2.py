
import pandas as pd
import sqlite3
import os

DB_FILE = 'database.db'

def test_stats(month_filter='2026-02', sede_filter='Bolivia'):
    try:
        year, month = month_filter.split('-')
        conn = sqlite3.connect(DB_FILE)
        servicios_df = pd.read_sql("SELECT * FROM servicios", conn)
        conn.close()

        print(f"Total rows read: {len(servicios_df)}")

        if sede_filter:
             servicios_df = servicios_df[servicios_df['sede'] == sede_filter]
             print(f"Rows after sede filter ({sede_filter}): {len(servicios_df)}")

        # Robust parsing
        servicios_df['fecha'] = pd.to_datetime(servicios_df['fecha'], errors='coerce')
        servicios_df = servicios_df.dropna(subset=['fecha'])
        
        servicios_month = servicios_df[(servicios_df['fecha'].dt.year == int(year)) & 
                                       (servicios_df['fecha'].dt.month == int(month))]
        
        print(f"Rows after month filter ({month_filter}): {len(servicios_month)}")
        if not servicios_month.empty:
            print(f"Sample dates: {servicios_month['fecha'].head(3).tolist()}")
        print(f"Total value: {servicios_month['valor'].sum()}")

    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error: {e}")

if __name__ == '__main__':
    test_stats('2026-02', 'Bolivia')

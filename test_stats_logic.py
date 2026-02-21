
import requests
import json

# This won't work if login is required and I don't have a session.
# But I can run the check internally by calling the function logic.

import pandas as pd
import sqlite3
from datetime import datetime
import os

DB_FILE = 'database.db'

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def test_stats(month_filter='2026-02', sede_filter='Bolivia'):
    try:
        year, month = month_filter.split('-')
        conn = get_db_connection()
        servicios_df = pd.read_sql("SELECT * FROM servicios", conn)
        productos_df = pd.read_sql("SELECT * FROM productos", conn)
        gastos_df = pd.read_sql("SELECT * FROM gastos", conn)
        inventario_df = pd.read_sql("SELECT * FROM inventario", conn)
        gastos_mensuales_df = pd.read_sql("SELECT * FROM gastos_mensuales", conn)
        conn.close()

        print(f"Total rows read: {len(servicios_df)}")

        if sede_filter:
             servicios_df = servicios_df[servicios_df['sede'] == sede_filter]
             productos_df = productos_df[productos_df['sede'] == sede_filter]
             print(f"Rows after sede filter ({sede_filter}): {len(servicios_df)}")

        servicios_df['fecha'] = pd.to_datetime(servicios_df['fecha'])
        servicios_month = servicios_df[(servicios_df['fecha'].dt.year == int(year)) & 
                                       (servicios_df['fecha'].dt.month == int(month))]
        
        print(f"Rows after month filter ({month_filter}): {len(servicios_month)}")
        print(f"Total value: {servicios_month['valor'].sum()}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    print("Testing 'Bolivia' for 2026-02:")
    test_stats('2026-02', 'Bolivia')
    print("\nTesting 'Garces Navas' for 2026-02:")
    test_stats('2026-02', 'Garces Navas')
    print("\nTesting 'Bolivia' for 2026-01:")
    test_stats('2026-01', 'Bolivia')


import pandas as pd
import sqlite3
import os
from datetime import datetime

DB_FILE = 'database.db'

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def test_full_stats(month_filter='2026-02', sede_filter='Bolivia'):
    try:
        year, month = month_filter.split('-')
        conn = get_db_connection()
        servicios_df = pd.read_sql("SELECT * FROM servicios", conn)
        productos_df = pd.read_sql("SELECT * FROM productos", conn)
        gastos_df = pd.read_sql("SELECT * FROM gastos", conn)
        inventario_df = pd.read_sql("SELECT * FROM inventario", conn)
        gastos_mensuales_df = pd.read_sql("SELECT * FROM gastos_mensuales", conn)
        conn.close()

        if sede_filter:
             servicios_df = servicios_df[servicios_df['sede'] == sede_filter]
             productos_df = productos_df[productos_df['sede'] == sede_filter]
             gastos_df = gastos_df[gastos_df['sede'] == sede_filter]
             inventario_df = inventario_df[inventario_df['sede'] == sede_filter]
             gastos_mensuales_df = gastos_mensuales_df[gastos_mensuales_df['sede'] == sede_filter]

        servicios_df['fecha'] = pd.to_datetime(servicios_df['fecha'], errors='coerce')
        productos_df['fecha'] = pd.to_datetime(productos_df['fecha'], errors='coerce')
        gastos_df['fecha'] = pd.to_datetime(gastos_df['fecha'], errors='coerce')
        
        # Drop rows with invalid dates if any
        servicios_df = servicios_df.dropna(subset=['fecha'])
        productos_df = productos_df.dropna(subset=['fecha'])
        gastos_df = gastos_df.dropna(subset=['fecha'])

        servicios_month = servicios_df[(servicios_df['fecha'].dt.year == int(year)) & 
                                       (servicios_df['fecha'].dt.month == int(month))]
        
        print(f"Month rows: {len(servicios_month)}")
        print(f"Total Sales: {servicios_month['valor'].sum()}")
        
        # Check nomina
        nomina = servicios_month.groupby('estilista')['comision'].sum().to_dict()
        print(f"Nomina: {nomina}")

    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error: {e}")

if __name__ == '__main__':
    test_full_stats('2026-02', 'Bolivia')

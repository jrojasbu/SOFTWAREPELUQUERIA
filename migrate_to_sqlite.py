
import sqlite3
import pandas as pd
import os
import sys

# Define file paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXCEL_FILE = os.path.join(BASE_DIR, 'database.xlsx')
DB_FILE = os.path.join(BASE_DIR, 'database.db')

def create_connection(db_file):
    """Create a database connection to the SQLite database specified by db_file."""
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Exception as e:
        print(e)
    return conn

def create_tables(conn):
    """Create tables in the SQLite database."""
    try:
        c = conn.cursor()
        
        # Servicios
        c.execute('''CREATE TABLE IF NOT EXISTS servicios (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        sede TEXT,
                        fecha TIMESTAMP,
                        estilista TEXT,
                        servicio TEXT,
                        valor REAL,
                        comision REAL,
                        metodo_pago TEXT
                    );''')
                    
        # Productos
        c.execute('''CREATE TABLE IF NOT EXISTS productos (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        sede TEXT,
                        fecha TIMESTAMP,
                        estilista TEXT,
                        producto TEXT,
                        marca TEXT,
                        descripcion TEXT,
                        valor REAL,
                        comision REAL,
                        metodo_pago TEXT
                    );''')

        # Gastos
        c.execute('''CREATE TABLE IF NOT EXISTS gastos (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        sede TEXT,
                        fecha TIMESTAMP,
                        descripcion TEXT,
                        valor REAL
                    );''')

        # Inventario
        c.execute('''CREATE TABLE IF NOT EXISTS inventario (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        sede TEXT,
                        producto TEXT,
                        marca TEXT,
                        descripcion TEXT,
                        cantidad REAL,
                        unidad TEXT,
                        valor REAL,
                        estado TEXT,
                        fecha_actualizacion TIMESTAMP
                    );''')

        # Citas
        c.execute('''CREATE TABLE IF NOT EXISTS citas (
                        id TEXT PRIMARY KEY,
                        sede TEXT,
                        fecha TEXT,
                        hora TEXT,
                        cliente TEXT,
                        telefono TEXT,
                        servicio TEXT,
                        notas TEXT,
                        estado TEXT
                    );''')

        # Gastos Mensuales
        c.execute('''CREATE TABLE IF NOT EXISTS gastos_mensuales (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        sede TEXT,
                        mes TEXT,
                        tipo TEXT,
                        valor REAL,
                        fecha_registro TIMESTAMP
                    );''')
        
        conn.commit()
        print("Tables created successfully.")
    except Exception as e:
        print(f"Error creating tables: {e}")

def migrate_data():
    if not os.path.exists(EXCEL_FILE):
        print(f"Error: {EXCEL_FILE} not found.")
        return

    conn = create_connection(DB_FILE)
    if conn is None:
        print("Error: Could not create database connection.")
        return

    create_tables(conn)

    try:
        # Migrate Servicios
        print("Migrating Servicios...")
        df = pd.read_excel(EXCEL_FILE, sheet_name='Servicios')
        # Rename columns to match SQL (lowercase, underscores if needed) if necessary, 
        # but pandas to_sql can handle it if we are careful. 
        # Actually, let's just insert row by row or use to_sql with 'append'.
        # We need to ensure column names map correctly.
        # Excel columns: Sede, Fecha, Estilista, Servicio, Valor, Comision, Metodo_Pago
        # Table columns: sede, fecha, estilista, servicio, valor, comision, metodo_pago
        df.columns = [c.lower().replace(' ', '_') for c in df.columns]
        df.to_sql('servicios', conn, if_exists='append', index=False)
        
        # Migrate Productos
        print("Migrating Productos...")
        df = pd.read_excel(EXCEL_FILE, sheet_name='Productos')
        df.columns = [c.lower().replace(' ', '_') for c in df.columns]
        df.to_sql('productos', conn, if_exists='append', index=False)

        # Migrate Gastos
        print("Migrating Gastos...")
        df = pd.read_excel(EXCEL_FILE, sheet_name='Gastos')
        df.columns = [c.lower().replace(' ', '_') for c in df.columns]
        df.to_sql('gastos', conn, if_exists='append', index=False)

        # Migrate Inventario
        print("Migrating Inventario...")
        df = pd.read_excel(EXCEL_FILE, sheet_name='Inventario')
        df.columns = [c.lower().replace(' ', '_') for c in df.columns]
        df.to_sql('inventario', conn, if_exists='append', index=False)

        # Migrate Citas
        print("Migrating Citas...")
        try:
            df = pd.read_excel(EXCEL_FILE, sheet_name='Citas')
            df.columns = [c.lower().replace(' ', '_') for c in df.columns]
            # Ensure ID is unique, if excel has duplicates (it shouldn't) it might fail if PK constraint
            df.to_sql('citas', conn, if_exists='append', index=False)
        except Exception as e:
            print(f"Error verifying Citas sheet: {e}")

        # Migrate Gastos Mensuales
        print("Migrating Gastos Mensuales...")
        try:
            df = pd.read_excel(EXCEL_FILE, sheet_name='GastosMensuales')
            df.columns = [c.lower().replace(' ', '_') for c in df.columns]
            df.to_sql('gastos_mensuales', conn, if_exists='append', index=False)
        except Exception as e:
            print(f"Error verifying GastosMensuales sheet: {e}")

        print("Migration completed successfully.")

    except Exception as e:
        print(f"Error during migration: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    migrate_data()

import pandas as pd
import os

DB_FILE = 'database.xlsx'

if os.path.exists(DB_FILE):
    try:
        df = pd.read_excel(DB_FILE, sheet_name='Citas')
        print("Columns:", df.columns.tolist())
        if 'Fecha' in df.columns:
            print("Fecha column types:")
            print(df['Fecha'].apply(type).unique())
            print("First 5 Fechas (raw):")
            print(df['Fecha'].head().tolist())
            
            # Simulate what the app does
            df['Fecha_str'] = df['Fecha'].astype(str)
            print("First 5 Fechas (astype(str)):")
            print(df['Fecha_str'].head().tolist())
            
        if 'Sede' in df.columns:
            print("Unique Sede values:")
            print(df['Sede'].unique().tolist())
            print("First 5 Sedes:")
            print(df['Sede'].head().tolist())
    except Exception as e:
        print(f"Error reading Excel: {e}")
else:
    print(f"{DB_FILE} not found.")

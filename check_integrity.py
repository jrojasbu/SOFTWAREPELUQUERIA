import pandas as pd
import os

DB_FILE = r'c:\Users\JROJASBU\OneDrive\Documentos\PROYECTOS\SOFTWARE PELUQUERIA\database.xlsx'

try:
    df = pd.read_excel(DB_FILE, sheet_name='Servicios')
    print(f"Total Rows read: {len(df)}")
    
    # Check for rows where 'Fecha' looks like a header or invalid
    if 'Fecha' in df.columns:
        # Find rows where Fecha is 'Fecha'
        header_rows = df[df['Fecha'] == 'Fecha']
        if not header_rows.empty:
            print(f"Found {len(header_rows)} rows that look like repeated headers!")
            print(header_rows.index.tolist())
        
        # Check for other non-date strings
        # We convert to string first to check content
        non_dates = df[pd.to_datetime(df['Fecha'], errors='coerce').isna()]
        print(f"Total rows with invalid dates: {len(non_dates)}")
        if len(non_dates) > 0:
            print("Sample values in 'Fecha' column for invalid rows:")
            print(non_dates['Fecha'].value_counts().head())
            
    # Check if 'Sede' column has unexpected values
    if 'Sede' in df.columns:
        print("\nSede value counts:")
        print(df['Sede'].value_counts())
        
except Exception as e:
    print(e)

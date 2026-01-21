import pandas as pd
import os

DB_FILE = r'c:\Users\JROJASBU\OneDrive\Documentos\PROYECTOS\SOFTWARE PELUQUERIA\database.xlsx'

try:
    print("Reading Excel...")
    df_servicios = pd.read_excel(DB_FILE, sheet_name='Servicios')
    
    if 'Sede' in df_servicios.columns:
        print(f"Unique Sede values: {df_servicios['Sede'].unique()}")
    else:
        print("Column 'Sede' not found!")
        
except Exception as e:
    print(f"Error: {e}")

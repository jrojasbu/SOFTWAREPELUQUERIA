import pandas as pd
from datetime import datetime
import numpy as np
import os

DB_FILE = r'c:\Users\JROJASBU\OneDrive\Documentos\PROYECTOS\SOFTWARE PELUQUERIA\database.xlsx'

if not os.path.exists(DB_FILE):
    print(f"File not found: {DB_FILE}")
    exit()

try:
    print("Reading Excel...")
    df_servicios = pd.read_excel(DB_FILE, sheet_name='Servicios')
    print(f"Total rows: {len(df_servicios)}")
    
    # Check columns
    print(f"Columns: {df_servicios.columns.tolist()}")
    
    # Check Sede match (assuming 'Principal')
    sede_filter = 'Bolivia'
    if 'Sede' in df_servicios.columns:
        print(f"filtering for Sede: {sede_filter}")
        # Strip whitespace just in case
        df_servicios['Sede'] = df_servicios['Sede'].astype(str).str.strip()
        df_servicios = df_servicios[df_servicios['Sede'] == sede_filter]
    
    print(f"Rows after sede filter: {len(df_servicios)}")
    
    # Date processing
    print("Processing dates...")
    # Print some raw dates first
    print("First 5 raw dates:")
    print(df_servicios['Fecha'].head())

    df_servicios['Fecha'] = pd.to_datetime(df_servicios['Fecha'], errors='coerce')
    
    # Check for Nat
    nats = df_servicios['Fecha'].isna().sum()
    print(f"Rows with invalid dates (Nat): {nats}")
    
    df_servicios = df_servicios.dropna(subset=['Fecha'])
    df_servicios['Fecha'] = df_servicios['Fecha'].dt.date
    
    today = datetime.now().date()
    sixty_days_ago = today - pd.Timedelta(days=60)
    print(f"Filtering dates from {sixty_days_ago} to {today}")
    
    df_recent = df_servicios[df_servicios['Fecha'] >= sixty_days_ago].copy()
    print(f"Rows in last 60 days: {len(df_recent)}")
    
    if not df_recent.empty:
        print("Sample recent rows:")
        print(df_recent[['Fecha', 'Servicio']].head())
        
        def categorize_service(name):
            name = str(name).lower()
            if 'corte' in name: return 'Corte'
            if 'tinte' in name or 'mechas' in name or 'color' in name or 'iluminaciones' in name or 'keratina' in name: return 'Tintura'
            if 'manicure' in name or 'pedicure' in name or 'uñas' in name or 'semi' in name: return 'Uñas'
            if 'depilacion' in name or 'cejas' in name or 'cera' in name or 'bigote' in name: return 'Depilación'
            return 'Otros'
            
        df_recent['Tipo'] = df_recent['Servicio'].apply(categorize_service)
        print("\nCategorization counts:")
        print(df_recent['Tipo'].value_counts())
        
        expected = ['Corte', 'Tintura', 'Uñas', 'Depilación']
        df_filtered = df_recent[df_recent['Tipo'].isin(expected)]
        print(f"\nRows matching expected types: {len(df_filtered)}")
    else:
        print("No recent data found. Showing last 5 dates in DB:")
        print(df_servicios['Fecha'].sort_values().tail())

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

import pandas as pd
from datetime import datetime
import numpy as np
import os

DB_FILE = r'c:\Users\JROJASBU\OneDrive\Documentos\PROYECTOS\SOFTWARE PELUQUERIA\database.xlsx'

try:
    print("Reading Excel...")
    df_servicios = pd.read_excel(DB_FILE, sheet_name='Servicios')
    
    # Check Sede match
    sede_filter = 'Bolivia'
    print(f"\nChecking for Sede: {sede_filter}")
    
    if 'Sede' in df_servicios.columns:
        df_sede = df_servicios[df_servicios['Sede'] == sede_filter].copy()
        print(f"Rows for {sede_filter}: {len(df_sede)}")
        
        if not df_sede.empty:
            df_sede['Fecha'] = pd.to_datetime(df_sede['Fecha'], errors='coerce')
            df_sede = df_sede.dropna(subset=['Fecha'])
            
            # Print date range
            min_date = df_sede['Fecha'].min()
            max_date = df_sede['Fecha'].max()
            print(f"Date range: {min_date} to {max_date}")
            
            today = datetime.now()
            print(f"App Today: {today}")
            
            sixty_days_ago = today - pd.Timedelta(days=60)
            
            df_recent = df_sede[df_sede['Fecha'] >= sixty_days_ago]
            print(f"Rows in last 60 days ({sixty_days_ago.date()} to {today.date()}): {len(df_recent)}")
            
            if not df_recent.empty:
                 # Check Service Categorization
                def categorize_service(name):
                    name = str(name).lower()
                    if 'corte' in name: return 'Corte'
                    if 'tinte' in name or 'mechas' in name or 'color' in name or 'iluminaciones' in name or 'keratina' in name: return 'Tintura'
                    if 'manicure' in name or 'pedicure' in name or 'uñas' in name or 'semi' in name: return 'Uñas'
                    if 'depilacion' in name or 'cejas' in name or 'cera' in name or 'bigote' in name: return 'Depilación'
                    return 'Otros'
                
                df_recent['Tipo'] = df_recent['Servicio'].apply(categorize_service)
                print("\nTypes found:")
                print(df_recent['Tipo'].value_counts())
                
        else:
            print("No rows found for this sede.")
            
except Exception as e:
    print(f"Error: {e}")

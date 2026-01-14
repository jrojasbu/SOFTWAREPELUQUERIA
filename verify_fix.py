import pandas as pd
import os
from datetime import datetime

DB_FILE = 'database.xlsx'

def verify_appointments(date_filter, sede_filter='Principal'):
    print(f"Verifying for Date: {date_filter}, Sede: {sede_filter}")
    try:
        df = pd.read_excel(DB_FILE, sheet_name='Citas')
        df = df.fillna('')
        
        print(f"Total rows in DB: {len(df)}")
        
        # Robust Sede filtering (Simulating the fix)
        if 'Sede' in df.columns:
            df['Sede'] = df['Sede'].astype(str).str.strip()
            df = df[df['Sede'] == sede_filter]
            print(f"Rows after Sede filter: {len(df)}")
        
        if date_filter:
            try:
                # Convert column to datetime, coerce errors to NaT
                df['Fecha_DT'] = pd.to_datetime(df['Fecha'], errors='coerce')
                
                # Create filter date object
                filter_date = pd.to_datetime(date_filter)
                
                # Filter rows where valid dates match
                # Check where expected format matches YYYY-MM-DD
                df = df[df['Fecha_DT'].dt.strftime('%Y-%m-%d') == filter_date.strftime('%Y-%m-%d')]
                print(f"Rows after Date filter: {len(df)}")
                print("Matches found:")
                print(df[['Fecha', 'Hora', 'Cliente', 'Sede']].to_string())
            except Exception as e:
                print(f"Date filtering error: {e}")

    except Exception as e:
        print(f"Error: {e}")

# Test with today's date or a known date from previous debug
# Previous debug showed: '2025-12-03', '2025-12-09', '2025-12-15'
verify_appointments('2025-12-15', 'Principal')
verify_appointments('2025-12-03', 'Bolivia')

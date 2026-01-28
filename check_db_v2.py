import pandas as pd
from datetime import datetime
import os

DB_FILE = r'c:\Users\JROJASBU\OneDrive\Documentos\PROYECTOS\SOFTWARE PELUQUERIA\database.xlsx'

if not os.path.exists(DB_FILE):
    print("Database file not found!")
    exit()

try:
    print("Reading Servicios sheet...")
    df = pd.read_excel(DB_FILE, sheet_name='Servicios')
    print(f'Total rows: {len(df)}')
    print(f'Columns: {df.columns.tolist()}')

    if 'Fecha' in df.columns:
        print("\n--- Date Analysis ---")
        # Show first few raw dates
        print("First 5 raw dates:\n", df['Fecha'].head().to_string())
        
        # Convert to datetime
        df['Fecha_DT'] = pd.to_datetime(df['Fecha'], errors='coerce')
        
        # Check invalid dates
        invalid_dates = df[df['Fecha_DT'].isna()]
        print(f"\nRows with invalid dates: {len(invalid_dates)}")
        if len(invalid_dates) > 0:
            print("Sample invalid dates:\n", invalid_dates['Fecha'].head().to_string())
            
        # Valid dates stats
        valid_df = df.dropna(subset=['Fecha_DT'])
        print(f"\nRows with valid dates: {len(valid_df)}")
        if not valid_df.empty:
            print(f"Date Range: {valid_df['Fecha_DT'].min()} to {valid_df['Fecha_DT'].max()}")
            
            # Group by year-month
            print("\nRecords per Month:")
            monthly_counts = valid_df['Fecha_DT'].dt.to_period('M').value_counts().sort_index()
            print(monthly_counts)
        else:
            print("No valid dates found!")
    else:
        print("Column 'Fecha' not found!")

except Exception as e:
    print(f"Error reading database: {e}")
    import traceback
    traceback.print_exc()

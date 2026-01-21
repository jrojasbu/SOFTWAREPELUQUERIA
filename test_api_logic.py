import pandas as pd
from datetime import datetime
import numpy as np

DB_FILE = 'database.xlsx'

try:
    df_servicios = pd.read_excel(DB_FILE, sheet_name='Servicios')
    sede_filter = 'Bolivia'
    if 'Sede' in df_servicios.columns:
        df_servicios = df_servicios[df_servicios['Sede'] == sede_filter]
    print(f"Rows for {sede_filter}: {len(df_servicios)}")
    
    df_servicios['Fecha'] = pd.to_datetime(df_servicios['Fecha'], errors='coerce')
    df_servicios = df_servicios.dropna(subset=['Fecha'])
    df_servicios['Fecha'] = df_servicios['Fecha'].dt.date
    
    today = datetime.now().date()
    sixty_days_ago = today - pd.Timedelta(days=60)
    df_recent = df_servicios[df_servicios['Fecha'] >= sixty_days_ago].copy()
    print(f"Recent rows: {len(df_recent)}")
    
    def categorize_service(name):
        name = str(name).lower()
        if 'corte' in name: return 'Corte'
        if 'tinte' in name or 'mechas' in name or 'color' in name or 'iluminaciones' in name or 'keratina' in name: return 'Tintura'
        if 'manicure' in name or 'pedicure' in name or 'uñas' in name or 'semi' in name: return 'Uñas'
        if 'depilacion' in name or 'cejas' in name or 'cera' in name or 'bigote' in name: return 'Depilación'
        return 'Otros'
    
    df_recent['Tipo'] = df_recent['Servicio'].apply(categorize_service)
    expected = ['Corte', 'Tintura', 'Uñas', 'Depilación']
    df_recent = df_recent[df_recent['Tipo'].isin(expected)]
    print(f"Filtered rows: {len(df_recent)}")
    
    daily_counts = df_recent.groupby(['Fecha', 'Tipo']).size().reset_index(name='Count')
    pivot_df = daily_counts.pivot(index='Fecha', columns='Tipo', values='Count').fillna(0).astype(int)
    for col in expected:
        if col not in pivot_df.columns:
            pivot_df[col] = 0
    
    print(f"Pivot shape: {pivot_df.shape}")
    print('Sample pivot:')
    print(pivot_df.head())
    
    historical = []
    for date_val, row in pivot_df.iterrows():
        entry = {'fecha': date_val.strftime('%Y-%m-%d')}
        for col in expected:
            entry[col] = int(row[col])
        historical.append(entry)
    
    print(f"Historical length: {len(historical)}")
    if historical:
        print('Sample:', historical[0])
    
except Exception as e:
    print('Error:', e)
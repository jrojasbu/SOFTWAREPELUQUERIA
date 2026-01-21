import pandas as pd
from datetime import datetime

DB_FILE = 'database.xlsx'

try:
    df = pd.read_excel(DB_FILE, sheet_name='Servicios')
    print('Total rows:', len(df))
    if 'Servicio' in df.columns:
        print('Unique Servicios:', df['Servicio'].unique()[:10])  # first 10
        print('All unique:', len(df['Servicio'].unique()))
    if 'Fecha' in df.columns:
        df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce')
        df = df.dropna(subset=['Fecha'])
        today = datetime.now()
        sixty_days_ago = today - pd.Timedelta(days=60)
        df_recent = df[df['Fecha'] >= sixty_days_ago]
        print('Rows in last 60 days:', len(df_recent))
        
        # Categorize services
        def categorize_service(name):
            name = str(name).lower()
            if 'corte' in name: return 'Corte'
            if 'tinte' in name or 'mechas' in name or 'color' in name or 'iluminaciones' in name or 'keratina' in name: return 'Tintura'
            if 'manicure' in name or 'pedicure' in name or 'uñas' in name or 'semi' in name: return 'Uñas'
            if 'depilacion' in name or 'cejas' in name or 'cera' in name or 'bigote' in name: return 'Depilación'
            return 'Otros'
        
        df_recent['Tipo'] = df_recent['Servicio'].apply(categorize_service)
        print('Service types count:')
        print(df_recent['Tipo'].value_counts())
        
        expected = ['Corte', 'Tintura', 'Uñas', 'Depilación']
        df_filtered = df_recent[df_recent['Tipo'].isin(expected)]
        print('Rows after filtering expected types:', len(df_filtered))
        
    else:
        print('No Fecha column')
except Exception as e:
    print('Error:', e)
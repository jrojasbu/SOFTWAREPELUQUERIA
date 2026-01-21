import pandas as pd
from datetime import datetime

DB_FILE = 'database.xlsx'
df = pd.read_excel(DB_FILE, sheet_name='Servicios')
print('Total filas:', len(df))

if 'Sede' in df.columns:
    print('Filas por sede:')
    for sede in df['Sede'].unique():
        count = len(df[df['Sede'] == sede])
        print(f'  {sede}: {count}')

# Filtrar a Bolivia
df_bolivia = df[df['Sede'] == 'Bolivia']
print('Filas para Bolivia:', len(df_bolivia))

# Convertir fecha
df_bolivia['Fecha'] = pd.to_datetime(df_bolivia['Fecha'], errors='coerce')
df_bolivia = df_bolivia.dropna(subset=['Fecha'])
df_bolivia['Fecha'] = df_bolivia['Fecha'].dt.date

# Filtrar 60 días
today = datetime.now().date()
sixty_ago = today - pd.Timedelta(days=60)
df_recent = df_bolivia[df_bolivia['Fecha'] >= sixty_ago]
print('Filas recientes Bolivia:', len(df_recent))

# Categorizar
def categorize(name):
    name = str(name).lower()
    if 'corte' in name: return 'Corte'
    if 'tinte' in name or 'mechas' in name or 'color' in name or 'iluminaciones' in name or 'keratina' in name: return 'Tintura'
    if 'manicure' in name or 'pedicure' in name or 'uñas' in name or 'semi' in name: return 'Uñas'
    if 'depilacion' in name or 'cejas' in name or 'cera' in name or 'bigote' in name: return 'Depilación'
    return 'Otros'

df_recent['Tipo'] = df_recent['Servicio'].apply(categorize)
expected = ['Corte', 'Tintura', 'Uñas', 'Depilación']
df_filtered = df_recent[df_recent['Tipo'].isin(expected)]
print('Filas filtradas Bolivia:', len(df_filtered))
print('Tipos en Bolivia:', df_filtered['Tipo'].value_counts())
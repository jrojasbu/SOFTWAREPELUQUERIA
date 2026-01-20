import pandas as pd
from datetime import datetime
import os

DB_FILE = 'database.xlsx'

def test_prediction():
    try:
        sede_filter = 'Bolivia' # Changing to Bolivia as seen in head()
        
        # Load data
        df_servicios = pd.read_excel(DB_FILE, sheet_name='Servicios')
        df_productos = pd.read_excel(DB_FILE, sheet_name='Productos')
        
        # Filter by sede
        df_servicios = df_servicios[df_servicios['Sede'] == sede_filter]
        df_productos = df_productos[df_productos['Sede'] == sede_filter]
        
        print(f"Servicios for {sede_filter}: {len(df_servicios)}")
        print(f"Productos for {sede_filter}: {len(df_productos)}")

        # Convert Fecha to datetime and floor to date
        df_servicios['Fecha'] = pd.to_datetime(df_servicios['Fecha']).dt.date
        df_productos['Fecha'] = pd.to_datetime(df_productos['Fecha']).dt.date
        
        # Aggregate by date
        daily_servicios = df_servicios.groupby('Fecha')['Valor'].sum()
        daily_productos = df_productos.groupby('Fecha')['Valor'].sum()
        
        # Combine
        daily_income = daily_servicios.add(daily_productos, fill_value=0).sort_index()
        
        # Convert to DataFrame
        income_df = daily_income.reset_index()
        income_df.columns = ['Fecha', 'Valor']
        
        # Get last 60 days of data
        today = datetime.now().date()
        sixty_days_ago = today - pd.Timedelta(days=60)
        income_df = income_df[income_df['Fecha'] >= sixty_days_ago]
        
        print(f"Income DF rows: {len(income_df)}")
        if not income_df.empty:
            print(income_df.head())
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    test_prediction()

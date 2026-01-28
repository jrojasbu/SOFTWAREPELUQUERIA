import pandas as pd

DB_FILE = r'c:\Users\JROJASBU\OneDrive\Documentos\PROYECTOS\SOFTWARE PELUQUERIA\database.xlsx'
df = pd.read_excel(DB_FILE, sheet_name='Servicios')

# Find string values starting with 2025-02
mask = df['Fecha'].astype(str).str.startswith('2025-02')
subset = df[mask]

if not subset.empty:
    val = subset['Fecha'].iloc[0]
    print(f"Value: '{val}'")
    print(f"Type: {type(val)}")
    print(f"Repr: {repr(val)}")
    
    try:
        dt = pd.to_datetime(val)
        print(f"Parsed: {dt}")
    except Exception as e:
        print(f"Parse Error: {e}")
        
    try:
        dt_coerce = pd.to_datetime(val, errors='coerce')
        print(f"Coerced: {dt_coerce}")
    except:
        pass
        
else:
    print("No matching rows found.")

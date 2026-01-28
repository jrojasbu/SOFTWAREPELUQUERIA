import pandas as pd
import traceback

DB_FILE = r'c:\Users\JROJASBU\OneDrive\Documentos\PROYECTOS\SOFTWARE PELUQUERIA\database.xlsx'
df = pd.read_excel(DB_FILE, sheet_name='Servicios')

print(f"Total rows: {len(df)}")
for idx, row in df.iterrows():
    val = row['Fecha']
    try:
        # Try strict parsing first to emulate app.py (it doesn't use errors='coerce' on the whole column usually, wait app.py 967 uses pd.to_datetime on column)
        # Actually app.py:987: servicios_df['Fecha'] = pd.to_datetime(servicios_df['Fecha'])
        # Pandas default behavior on Series is 'raise' on error? No, it's 'raise' by default for scalars, but for Series?
        # pd.to_datetime(arg, errors='raise') is default.
        
        pd.to_datetime(val)
    except Exception as e:
        print(f"Row {idx} Failed: Value='{val}', Type={type(val)}")
        print(f"Error: {e}")
        # convert to bytes to see hidden chars
        if isinstance(val, str):
            print(f"Bytes: {val.encode('utf-8')}")
        break

# Also check if mass conversion fails
try:
    print("Attempting mass conversion...")
    pd.to_datetime(df['Fecha'])
    print("Mass conversion successful!")
except Exception as e:
    print("Mass conversion failed!")
    print(str(e)[:200]) # First 200 chars of error

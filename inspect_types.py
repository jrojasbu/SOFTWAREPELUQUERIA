import pandas as pd
import os

DB_FILE = r'c:\Users\JROJASBU\OneDrive\Documentos\PROYECTOS\SOFTWARE PELUQUERIA\database.xlsx'

df = pd.read_excel(DB_FILE, sheet_name='Servicios')

print("Types in Fecha column:")
print(df['Fecha'].apply(type).value_counts())

print("\nSample of values that are strings:")
strings = df[df['Fecha'].apply(lambda x: isinstance(x, str))]['Fecha']
if not strings.empty:
    print(strings.head(10).tolist())

print("\nSample of values that are datetime:")
dts = df[df['Fecha'].apply(lambda x: isinstance(x, (pd.Timestamp, pd.DatetimeIndex)))] # Pandas might convert to Timestamp
# Check basic python datetime too just in case
import datetime
dts_py = df[df['Fecha'].apply(lambda x: isinstance(x, datetime.datetime))]

if not dts_py.empty:
    print(dts_py['Fecha'].head().tolist())

print("\nTrying to parse the specific string '2025-02-15':")
try:
    print(pd.to_datetime('2025-02-15'))
    print("Direct string parsing works.")
except:
    print("Direct string parsing failed.")

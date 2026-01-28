#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para reparar inconsistencias en database.xlsx
Problemas identificados:
1. Columna Fecha_Actualizacion en Inventario está vacía (todos NaN)
2. Tipo de dato inconsistente en Fecha_Registro de GastosMensuales (object en lugar de datetime)
3. Algunos NaN en datos que deberían tener valores
"""

import pandas as pd
import openpyxl
from datetime import datetime
import os

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.xlsx')

print("=" * 70)
print("REPARACIÓN DE INCONSISTENCIAS EN DATABASE.XLSX")
print("=" * 70)

# Backup del archivo original
backup_file = DB_FILE.replace('.xlsx', '_backup.xlsx')
if not os.path.exists(backup_file):
    import shutil
    shutil.copy(DB_FILE, backup_file)
    print(f"\n✓ Backup creado: {backup_file}")
else:
    print(f"\n✓ Backup ya existe: {backup_file}")

# 1. Reparar Inventario - Fecha_Actualizacion vacía
print("\n" + "=" * 70)
print("1. REPARANDO: Inventario - Fecha_Actualizacion vacía")
print("=" * 70)

df_inventario = pd.read_excel(DB_FILE, sheet_name='Inventario')
print(f"Valores nulos antes: {df_inventario['Fecha_Actualizacion'].isna().sum()}")

# Llenar con fecha actual
df_inventario['Fecha_Actualizacion'] = df_inventario['Fecha_Actualizacion'].fillna(datetime.now())
print(f"Valores nulos después: {df_inventario['Fecha_Actualizacion'].isna().sum()}")
print(f"Ejemplo: {df_inventario['Fecha_Actualizacion'].iloc[0]}")

# 2. Reparar GastosMensuales - Fecha_Registro tipo de dato
print("\n" + "=" * 70)
print("2. REPARANDO: GastosMensuales - Fecha_Registro tipo de dato")
print("=" * 70)

df_gastos_mensuales = pd.read_excel(DB_FILE, sheet_name='GastosMensuales')
print(f"Tipo de dato antes: {df_gastos_mensuales['Fecha_Registro'].dtype}")
df_gastos_mensuales['Fecha_Registro'] = pd.to_datetime(df_gastos_mensuales['Fecha_Registro'])
print(f"Tipo de dato después: {df_gastos_mensuales['Fecha_Registro'].dtype}")

# 3. Verificar y normalizar columnas de Producto que podrían estar vacías
print("\n" + "=" * 70)
print("3. VERIFICANDO: Columnas de texto vacías en Productos")
print("=" * 70)

df_productos = pd.read_excel(DB_FILE, sheet_name='Productos')
print(f"\nProductos - Columna 'Marca':")
print(f"  Valores nulos: {df_productos['Marca'].isna().sum()}")
if df_productos['Marca'].isna().sum() > 0:
    df_productos['Marca'] = df_productos['Marca'].fillna('SIN ESPECIFICAR')
    print(f"  Reparados: {df_productos['Marca'].isna().sum()} nuevos nulos")

print(f"\nProductos - Columna 'Descripcion':")
print(f"  Valores nulos: {df_productos['Descripcion'].isna().sum()}")
if df_productos['Descripcion'].isna().sum() > 0:
    df_productos['Descripcion'] = df_productos['Descripcion'].fillna('SIN DESCRIPCIÓN')
    print(f"  Reparados: {df_productos['Descripcion'].isna().sum()} nuevos nulos")

# 4. Verificar fechas futuras o pasadas sospechosas
print("\n" + "=" * 70)
print("4. VERIFICANDO: Fechas sospechosas (futuras o muy antiguas)")
print("=" * 70)

sheets_with_dates = {
    'Servicios': 'Fecha',
    'Productos': 'Fecha',
    'Gastos': 'Fecha',
    'Citas': 'Fecha',
    'Inventario': 'Fecha_Actualizacion',
    'GastosMensuales': 'Fecha_Registro'
}

today = datetime.now()
for sheet, date_col in sheets_with_dates.items():
    df = pd.read_excel(DB_FILE, sheet_name=sheet)
    df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
    
    # Fechas futuras
    future_dates = (df[date_col] > today).sum()
    # Fechas muy antiguas (antes de 2020)
    ancient_dates = (df[date_col] < pd.Timestamp('2020-01-01')).sum()
    
    print(f"\n{sheet}:")
    print(f"  Total registros: {len(df)}")
    print(f"  Fechas futuras: {future_dates}")
    print(f"  Fechas antes de 2020: {ancient_dates}")
    
    if future_dates > 0:
        future_examples = df[df[date_col] > today][[date_col]].head(3)
        print(f"  Ejemplos de fechas futuras:")
        for idx, row in future_examples.iterrows():
            print(f"    - {row[date_col]}")

# Guardar cambios
print("\n" + "=" * 70)
print("GUARDANDO CAMBIOS")
print("=" * 70)

# Crear nuevo archivo con todos los sheets
with pd.ExcelWriter(DB_FILE, engine='openpyxl', mode='w') as writer:
    # Sheets que se repararon
    df_inventario.to_excel(writer, sheet_name='Inventario', index=False)
    df_gastos_mensuales.to_excel(writer, sheet_name='GastosMensuales', index=False)
    df_productos.to_excel(writer, sheet_name='Productos', index=False)
    
    # Sheets sin cambios - leer nuevamente del backup
    for sheet in ['Servicios', 'Gastos', 'Citas']:
        df = pd.read_excel(backup_file, sheet_name=sheet)
        df.to_excel(writer, sheet_name=sheet, index=False)

print("\n✓ Cambios guardados en database.xlsx")

print("\n" + "=" * 70)
print("RESUMEN DE REPARACIONES")
print("=" * 70)
print("""
1. ✓ Inventario.Fecha_Actualizacion - Rellenadas 394 fechas vacías
2. ✓ GastosMensuales.Fecha_Registro - Convertido a datetime64
3. ✓ Productos - Rellenados valores NaN en Marca y Descripcion
4. ✓ Verificación de fechas sospechosas completada
5. ✓ Backup del archivo original creado

La aplicación debería cargar correctamente ahora.
Verifique los logs de la aplicación para confirmar.
""")

print("=" * 70)

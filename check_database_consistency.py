#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pandas as pd
import openpyxl
from datetime import datetime
import os

print("=" * 60)
print("VERIFICACIÓN DE CONSISTENCIA DE DATABASE.XLSX")
print("=" * 60)

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.xlsx')
print(f"\nArchivo: {DB_FILE}")
print(f"Existe: {os.path.exists(DB_FILE)}")

if not os.path.exists(DB_FILE):
    print("ERROR: El archivo no existe")
    exit(1)

# Cargar sheets
xl_file = pd.ExcelFile(DB_FILE)
print(f"\nSheets encontrados: {xl_file.sheet_names}")

for sheet in xl_file.sheet_names:
    print(f"\n{'=' * 60}")
    print(f"SHEET: {sheet}")
    print('=' * 60)
    
    try:
        df = pd.read_excel(DB_FILE, sheet_name=sheet)
        print(f"Filas: {len(df)}, Columnas: {len(df.columns)}")
        print(f"\nColumnas: {df.columns.tolist()}")
        
        # Buscar columnas de fecha
        date_cols = [col for col in df.columns if 'fecha' in col.lower() or 'date' in col.lower()]
        if date_cols:
            print(f"\nColumnas de FECHA encontradas: {date_cols}")
            for col in date_cols:
                print(f"\n  {col}:")
                print(f"    Tipo de dato: {df[col].dtype}")
                print(f"    Valores nulos: {df[col].isna().sum()}")
                print(f"    Valores únicos: {df[col].nunique()}")
                
                # Mostrar primeros valores
                non_null = df[df[col].notna()][col].head(5)
                if len(non_null) > 0:
                    print(f"    Ejemplos (primeros 5):")
                    for i, val in enumerate(non_null, 1):
                        try:
                            if isinstance(val, str):
                                parsed = pd.to_datetime(val)
                            else:
                                parsed = val
                            print(f"      {i}. {repr(val)} -> {parsed}")
                        except Exception as e:
                            print(f"      {i}. {repr(val)} -> ERROR: {str(e)[:50]}")
        
        # Mostrar primeros datos
        if len(df) > 0:
            print(f"\nPrimeras 3 filas:")
            print(df.head(3).to_string())
        else:
            print("\n>>> SHEET VACÍO <<<")
            
    except Exception as e:
        import traceback
        print(f"ERROR al leer sheet: {e}")
        traceback.print_exc()

print("\n" + "=" * 60)
print("VERIFICACIÓN COMPLETADA")
print("=" * 60)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test final de carga de datos"""
import pandas as pd
import os

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.xlsx')

print("=" * 60)
print("✓ TEST FINAL DE CARGA DE DATOS")
print("=" * 60)

try:
    xl = pd.ExcelFile(DB_FILE)
    print(f"\n✓ Base de datos cargada correctamente")
    print(f"  Ubicación: {DB_FILE}")
    print(f"\n  Sheets encontrados:")
    
    total_registros = 0
    for sheet in xl.sheet_names:
        df = pd.read_excel(DB_FILE, sheet_name=sheet)
        total = len(df)
        total_registros += total
        print(f"    - {sheet:20} : {total:5} registros")
    
    print(f"\n  TOTAL DE REGISTROS: {total_registros}")
    print(f"\n✓ Verificación completada exitosamente")
    print(f"  La aplicación puede cargar los datos sin problemas")
    
except Exception as e:
    print(f"\n✗ ERROR: {e}")
    import traceback
    traceback.print_exc()

print("=" * 60)

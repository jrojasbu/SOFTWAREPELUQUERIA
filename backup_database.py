"""
Backup Script for Magical Hair Database
Creates dated backups of database.db (siempre en la carpeta del ejecutable)
"""

import sys
import os
import shutil
from pathlib import Path
from datetime import datetime

# Carpeta del ejecutable o del script (misma carpeta que database.db)
if getattr(sys, 'frozen', False):
    PROJECT_DIR = Path(sys.executable).parent.absolute()
else:
    PROJECT_DIR = Path(__file__).parent.absolute()

# Base de datos SQLite - siempre en la carpeta del ejecutable
SOURCE_DATABASE = PROJECT_DIR / "database.db"

# Carpeta de respaldos
BACKUP_FOLDER = PROJECT_DIR / "Backup"


def create_backup():
    """Crea respaldo con fecha de database.db."""
    today = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    
    BACKUP_FOLDER.mkdir(exist_ok=True)
    print(f"Carpeta de respaldo: {BACKUP_FOLDER}")
    
    if SOURCE_DATABASE.exists():
        backup_name = f"database_{today}.db"
        backup_path = BACKUP_FOLDER / backup_name
        shutil.copy2(SOURCE_DATABASE, backup_path)
        print(f"Respaldo creado: {backup_path}")
    else:
        print(f"Advertencia: {SOURCE_DATABASE} no encontrado.")
    
    print("\nRespaldo completado.")


if __name__ == "__main__":
    create_backup()

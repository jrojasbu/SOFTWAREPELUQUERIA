# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules

hiddenimports = ['openpyxl', 'pandas', 'matplotlib', 'PIL', 'reportlab', 'reportlab.graphics.barcode', 'reportlab.graphics.barcode.code128', 'reportlab.graphics.barcode.code93', 'reportlab.graphics.barcode.code39', 'reportlab.graphics.barcode.usps', 'reportlab.graphics.barcode.usps4s', 'reportlab.graphics.barcode.ecc200datamatrix', 'reportlab.graphics.barcode.qr', 'reportlab.graphics.barcode.eanbc', 'reportlab.graphics.barcode.lto', 'reportlab.graphics.barcode.common', 'html5lib']
hiddenimports += collect_submodules('reportlab.graphics.barcode')


a = Analysis(
    ['run.py'],
    pathex=[],
    binaries=[],
    datas=[('templates', 'templates'), ('static', 'static')],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='MagicalHairApp_Debug_v3.1',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

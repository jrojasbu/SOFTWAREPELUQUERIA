# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules

hiddenimports = ['openpyxl', 'pandas', 'matplotlib', 'PIL', 'reportlab', 'html5lib', 'xhtml2pdf']
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
    name='MagicalHairApp_v3.0',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

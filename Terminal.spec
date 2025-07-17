# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Serial Terminal standalone application
"""

block_cipher = None

a = Analysis(
    ['terminal_main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('ui/theme', 'ui/theme'),
        ('ui/windows', 'ui/windows'),
        ('ui/dialogs', 'ui/dialogs'),
        ('core', 'core'),
    ],
    hiddenimports=[
        'PyQt6.QtSvg',
        'PyQt6.QtWidgets',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'serial',
        'serial.tools.list_ports',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Serial Terminal',
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
    icon='icon.ico',
    uac_admin=False,  # Terminal doesn't need admin privileges unlike main app
)
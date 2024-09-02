# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.win32 import versioninfo as vi

version_file = vi.VSVersionInfo(
    ffi=vi.FixedFileInfo(
        filevers=(1, 0, 0, 0),
        prodvers=(1, 0, 0, 0),
        mask=0x3f,
        flags=0x0,
        OS=0x4,
        fileType=0x1,
        subtype=0x0,
        date=(0, 0)
    ),
    kids=[
        vi.StringFileInfo([
            vi.StringTable(
                u'040904B0', [
                    vi.StringStruct(u'FileDescription', u'Simple Wuthering Waves Inventory scanner.'),
                    vi.StringStruct(u'FileVersion', u'1.0.0.0'),
                    vi.StringStruct(u'InternalName', u'WuWaInventoryKamera'),
                    vi.StringStruct(u'OriginalFilename', u'WuWa_Inventory_Kamera.exe'),
                    vi.StringStruct(u'ProductName', u'WuWa Inventory Kamera'),
                    vi.StringStruct(u'ProductVersion', u'1.0.0.0')
                ])
        ]),
        vi.VarFileInfo([vi.VarStruct(u'Translation', [0x0409, 0x04B0])])
    ]
)

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('assets', 'assets'),
        ('Tesseract-OCR', 'Tesseract-OCR'),
    ],
    hiddenimports=[],
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
    [],
    exclude_binaries=True,
    name='WuWa Inventory Kamera',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon='./assets/icon.ico',
    version=version_file
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='main',
    bindir='_internal'
)

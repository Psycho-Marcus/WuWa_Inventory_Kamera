# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.win32 import versioninfo as vi
from pathlib import Path
import importlib.util

version = (1, 6, 0, 0)

version_file = vi.VSVersionInfo(
    ffi=vi.FixedFileInfo(
        filevers=version,
        prodvers=version,
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
                    vi.StringStruct(u'FileVersion', '.'.join(map(str, version))),
                    vi.StringStruct(u'InternalName', u'WuWaInventoryKamera'),
                    vi.StringStruct(u'OriginalFilename', u'WuWa_Inventory_Kamera.exe'),
                    vi.StringStruct(u'ProductName', u'WuWa Inventory Kamera'),
                    vi.StringStruct(u'ProductVersion', '.'.join(map(str, version)))
                ])
        ]),
        vi.VarFileInfo([vi.VarStruct(u'Translation', [0x0409, 0x04B0])])
    ]
)

def check_package_exists(package_name):
    package_spec = importlib.util.find_spec(package_name)
    return package_spec is not None

if check_package_exists('rapidocr_onnxruntime'):
    package_name = 'rapidocr_onnxruntime'
    package = __import__(package_name)
    install_dir = Path(package.__file__).resolve().parent

    file_paths = {
        'onnx': list(install_dir.rglob('*.onnx')),
        'txt': list(install_dir.rglob('*.txt')),
        'yaml': list(install_dir.rglob('*.yaml'))
    }

    add_data = []
    for ext in ['onnx', 'txt']:
        for path in file_paths[ext]:
            rel_dir = path.parent.relative_to(install_dir)
            add_data.append((str(path.parent), f'{package_name}/{rel_dir}'))

    for path in file_paths['yaml']:
        rel_dir = path.parent.relative_to(install_dir)
        if rel_dir == Path('.'):
            add_data.append((str(path.parent / '*.yaml'), package_name))
        else:
            add_data.append((str(path.parent / '*.yaml'), f'{package_name}/{rel_dir}'))

    add_data = list(set(add_data))
else:
    add_data = []

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('assets', 'assets'),
        *add_data
    ],
    hiddenimports=['babel.dates', 'babel.numbers'],
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

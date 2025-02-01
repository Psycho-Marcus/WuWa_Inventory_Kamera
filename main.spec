# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.win32 import versioninfo as vi
from pathlib import Path
import importlib.util

class VersionInfo:
    def __init__(self, versionTuple):
        self.version = versionTuple
        self.versionStr = '.'.join(map(str, versionTuple))
        
    def createVersionInfo(self):
        return vi.VSVersionInfo(
            ffi=self._createFixedFileInfo(),
            kids=self._createVersionStrings()
        )
    
    def _createFixedFileInfo(self):
        return vi.FixedFileInfo(
            filevers=self.version,
            prodvers=self.version,
            mask=0x3f,
            flags=0x0,
            OS=0x4,
            fileType=0x1,
            subtype=0x0,
            date=(0, 0)
        )
    
    def _createVersionStrings(self):
        return [
            vi.StringFileInfo([
                vi.StringTable(
                    u'040904B0', [
                        vi.StringStruct(u'FileDescription', u''),
                        vi.StringStruct(u'FileVersion', self.versionStr),
                        vi.StringStruct(u'InternalName', u'WuWaInventoryKamera'),
                        vi.StringStruct(u'OriginalFilename', u'WuWa_Inventory_Kamera.exe'),
                        vi.StringStruct(u'ProductName', u'WuWa Inventory Kamera'),
                        vi.StringStruct(u'ProductVersion', self.versionStr)
                    ])
            ]),
            vi.VarFileInfo([vi.VarStruct(u'Translation', [0x0409, 0x04B0])])
        ]

class PackageDataCollector:
    def __init__(self, packageName):
        self.packageName = packageName
        self.package = __import__(packageName)
        self.installDir = Path(self.package.__file__).resolve().parent
        
    def collectDataFiles(self):
        extensions = {
            'onnx': '*.onnx',
            'txt': '*.txt',
            'yaml': '*.yaml'
        }
        
        addData = []
        for ext, pattern in extensions.items():
            for path in self.installDir.rglob(pattern):
                relDir = path.parent.relative_to(self.installDir)
                if ext == 'yaml' and relDir == Path('.'):
                    addData.append((str(path.parent / pattern), self.packageName))
                else:
                    targetDir = f'{self.packageName}/{relDir}' if relDir != Path('.') else self.packageName
                    addData.append((str(path.parent), targetDir))
        
        return list(set(addData))

versionInfo = VersionInfo((1, 7, 0, 0))
packageData = PackageDataCollector('rapidocr_onnxruntime')

analysisData = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('assets', 'assets'),
        *packageData.collectDataFiles()
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyzData = PYZ(analysisData.pure)

exeData = EXE(
    pyzData,
    analysisData.scripts,
    [],
    exclude_binaries=True,
    name='WuWa Inventory Kamera',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon='./assets/icon.ico',
    version=versionInfo.createVersionInfo()
)

collectData = COLLECT(
    exeData,
    analysisData.binaries,
    analysisData.zipfiles,
    analysisData.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name=f"v{versionInfo.versionStr[:5]}",
    bindir='_internal'
)
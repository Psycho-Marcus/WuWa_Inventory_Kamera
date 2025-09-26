import cx_Freeze

executables = [
    cx_Freeze.Executable(
        "main.py",
        base="Win32GUI",
        target_name="WuWa Inventory Kamera",
        icon="assets/icon.ico",
        uac_admin=True
    )
]

cx_Freeze.setup(
    name="WuWa Inventory Kamera",
    version="1.7.1",
    options={
        "build_exe": {
            "packages": ["rapidocr_onnxruntime"],
            "excludes": [
                "tkinter", "unittest", "email", "html",
                "xml", "distutils", "setuptools", "pip", "wheel"
            ],
            "include_files": [
                ("assets", "assets")
            ],
            "optimize": 2,
            "build_exe": "dist/v1.7.1",
            "silent_level": 0,
            "include_msvcr": True,
        }
    },
    executables=executables
)
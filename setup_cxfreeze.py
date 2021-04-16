import sys

from apyk.win_main import version
from cx_Freeze import Executable, setup

includefiles = ['LICENSE', 'README.md']

base = None

if sys.platform == 'win32':
    base = 'Win32GUI'

executables = [Executable(
    script='apyk/win_main.py',
    target_name='apyk.exe',
    copyright='Copyright (C) 2021 Pedro Torcatt',
    base=base,
    icon='apyk/icon.png'
)]

setup(
    version=version,
    name='APyK',
    description='APyK is a program with which you will be able to backup your applications from your computer.',
    executables=executables,
    options={
        'build_exe': {
            # 'zip_include_packages': ['PyQt5'],
            'include_files': includefiles,
            'excludes': ['tkinter'],
            'optimize': 2,
            'include_msvcr': True
        }
    },
)

# -*- mode: python ; coding: utf-8 -*-
"""
幽梦个人助手 - PyInstaller打包配置
版本: 1.0.0
"""

import os
import sys

# 项目根目录
PROJ_ROOT = os.path.dirname(os.path.abspath(SPEC))

# 应用信息
APP_NAME = '幽梦个人助手'
APP_VERSION = '1.0.0'

block_cipher = None

# 需要打包的数据文件
datas = [
    # 资源文件
    (os.path.join(PROJ_ROOT, 'resources'), 'resources'),
]

# 隐式导入的模块（PyQt5相关）
hiddenimports = [
    'PyQt5',
    'PyQt5.QtCore',
    'PyQt5.QtGui',
    'PyQt5.QtWidgets',
    'PyQt5.sip',
    'sqlite3',
]

# 排除不需要的模块（减小体积）
excludes = [
    'tkinter',
    'matplotlib',
    'numpy',
    'pandas',
    'scipy',
    'PIL',
    'cv2',
    'pytest',
    'unittest',
]

a = Analysis(
    ['main.py'],
    pathex=[PROJ_ROOT],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher,
)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name=APP_NAME,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 隐藏控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # Windows特定设置
    version_file=None,
    icon=os.path.join(PROJ_ROOT, 'resources', 'icons', 'app.ico'),
)

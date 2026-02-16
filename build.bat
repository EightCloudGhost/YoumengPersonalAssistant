@echo off
chcp 65001 >nul
echo ========================================
echo   幽梦个人助手 - 打包脚本 v1.0.0
echo ========================================
echo.

:: 检查Python环境
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python，请先安装Python 3.7+
    pause
    exit /b 1
)

:: 检查PyInstaller
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo [信息] 正在安装PyInstaller...
    pip install pyinstaller
    if errorlevel 1 (
        echo [错误] PyInstaller安装失败
        pause
        exit /b 1
    )
)

echo.
echo [步骤1] 开始打包EXE...
echo.

:: 清理旧的构建文件
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"

:: 执行PyInstaller打包
pyinstaller YoumengAssistant.spec --clean

if errorlevel 1 (
    echo.
    echo [错误] EXE打包失败，请检查错误信息
    pause
    exit /b 1
)

echo.
echo [完成] EXE打包成功: dist\幽梦个人助手.exe
echo.

:: 检查是否需要创建安装程序
set /p CREATE_INSTALLER="是否创建安装程序？(Y/N): "
if /i "%CREATE_INSTALLER%" neq "Y" (
    echo.
    echo 已跳过安装程序创建。
    explorer dist
    pause
    exit /b 0
)

:: 检查Inno Setup
set ISCC_PATH=
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
    set "ISCC_PATH=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
) else if exist "C:\Program Files\Inno Setup 6\ISCC.exe" (
    set "ISCC_PATH=C:\Program Files\Inno Setup 6\ISCC.exe"
)

if "%ISCC_PATH%"=="" (
    echo.
    echo [警告] 未找到Inno Setup 6，无法创建安装程序。
    echo 请从以下地址下载安装Inno Setup 6：
    echo https://jrsoftware.org/isdl.php
    echo.
    echo EXE文件已生成在: dist\幽梦个人助手.exe
    explorer dist
    pause
    exit /b 0
)

echo.
echo [步骤2] 开始创建安装程序...
echo.

:: 创建输出目录
if not exist "installer_output" mkdir "installer_output"

:: 执行Inno Setup编译
"%ISCC_PATH%" installer.iss

if errorlevel 1 (
    echo.
    echo [错误] 安装程序创建失败
    pause
    exit /b 1
)

echo.
echo ========================================
echo   全部完成！
echo   EXE文件: dist\幽梦个人助手.exe
echo   安装程序: installer_output\幽梦个人助手_安装程序_v1.0.0.exe
echo ========================================
echo.

:: 打开输出目录
explorer installer_output

pause

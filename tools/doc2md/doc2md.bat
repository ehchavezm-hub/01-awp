@echo off
chcp 65001 >nul
title doc2md
cd /d "%~dp0"

if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" -c "import docling" >nul 2>&1 && goto abrir
)

echo ============================================================
echo  Primera vez: instalando doc2md.
echo  Tarda varios minutos (descarga unos 2 GB). Solo ocurre una vez.
echo ============================================================
where python >nul 2>&1
if errorlevel 1 (
    echo.
    echo No se encontro Python. Instalalo desde https://www.python.org/downloads/
    echo y marca "Add Python to PATH" durante la instalacion. Luego vuelve a abrir doc2md.
    pause
    exit /b 1
)
if not exist ".venv\Scripts\python.exe" python -m venv .venv
".venv\Scripts\python.exe" -m pip install --upgrade pip
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo La instalacion fallo. Copia el mensaje de arriba para revisarlo.
    rmdir /s /q .venv
    pause
    exit /b 1
)
rem Acceso directo en el escritorio (si Windows lo permite).
powershell -NoProfile -ExecutionPolicy Bypass -Command "$s=(New-Object -ComObject WScript.Shell).CreateShortcut([Environment]::GetFolderPath('Desktop')+'\doc2md.lnk'); $s.TargetPath='%~dp0doc2md.bat'; $s.WorkingDirectory='%~dp0'; $s.IconLocation='%SystemRoot%\System32\imageres.dll,97'; $s.Save()" >nul 2>&1
echo.
echo Instalacion terminada. Se creo el acceso directo "doc2md" en tu escritorio.

:abrir
".venv\Scripts\python.exe" -m doc2md.app
if errorlevel 1 pause

@echo off
chcp 65001 >nul
cd /d "%~dp0"
where python >nul 2>&1
if errorlevel 1 (
    echo No se encontro Python. Instalalo desde https://www.python.org/downloads/
    echo y marca "Add Python to PATH" durante la instalacion.
    pause
    exit /b 1
)
if not exist ".venv\Scripts\python.exe" (
    echo Creando el entorno...
    python -m venv .venv
)
echo Instalando Docling. Puede tardar varios minutos ^(descarga unos 2 GB^)...
".venv\Scripts\python.exe" -m pip install --upgrade pip
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo La instalacion fallo. Copia el mensaje de arriba para revisarlo.
    pause
    exit /b 1
)
echo.
echo Instalacion terminada. Para convertir, arrastra tus PDF o EPUB sobre convertir.bat
pause

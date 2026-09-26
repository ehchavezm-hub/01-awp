@echo off
chcp 65001 >nul
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    echo Primero ejecuta instalar.bat
    pause
    exit /b 1
)
if "%~1"=="" (
    echo Arrastra uno o varios archivos PDF o EPUB sobre convertir.bat
    pause
    exit /b 1
)
echo Convirtiendo... Puede tardar varios minutos por documento. No cierres esta ventana.
echo.
".venv\Scripts\python.exe" -m doc2md %* -o "%~dp0resultados"
echo.
echo Resultados en: %~dp0resultados
pause

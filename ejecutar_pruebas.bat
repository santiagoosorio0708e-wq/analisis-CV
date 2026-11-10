@echo off
echo ========================================================
echo          Ejecutando Pruebas Unitarias y Cobertura
echo ========================================================
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] No se encontro el entorno virtual .venv.
    pause
    exit /b 1
)

echo 1. Corriendo suite de pytest con cobertura...
.\.venv\Scripts\python.exe -m pytest -v --cov=app/intermedio/cv_analyzer

echo.
echo ========================================================
echo          Verificando Calidad de Codigo con Ruff
echo ========================================================
.\.venv\Scripts\ruff.exe check .

echo.
echo ========================================================
echo          Verificando Compilacion y Dependencias
echo ========================================================
.\.venv\Scripts\python.exe -m compileall -q app tests
.\.venv\Scripts\python.exe -m pip check

echo.
echo Verificaciones completadas exitosamente.
pause

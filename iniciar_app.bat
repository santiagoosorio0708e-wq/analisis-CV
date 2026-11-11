@echo off
echo ========================================================
echo          Iniciando CV Analyzer con Google Gemini
echo ========================================================
cd /d "%~dp0"

if not exist ".env" (
    echo [AVISO] No se encontro el archivo .env. Creando a partir de .env.example...
    copy .env.example .env
    echo Por favor configura tu GEMINI_API_KEY en el archivo .env antes de analizar.
)

echo Iniciando la aplicacion en http://127.0.0.1:8502 ...
where py >nul 2>&1
if %ERRORLEVEL% equ 0 (
    py -m streamlit run app\intermedio\cv_analyzer\app.py --server.port=8502 --server.address=127.0.0.1
) else (
    .\.venv\Scripts\python.exe -m streamlit run app\intermedio\cv_analyzer\app.py --server.port=8502 --server.address=127.0.0.1
)
pause

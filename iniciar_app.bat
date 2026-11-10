@echo off
echo ========================================================
echo          Iniciando CV Analyzer con Google Gemini
echo ========================================================
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] No se encontro el entorno virtual .venv.
    echo Creando entorno virtual e instalando dependencias...
    py -m venv .venv
    .\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
)

if not exist ".env" (
    echo [AVISO] No se encontro el archivo .env. Creando a partir de .env.example...
    copy .env.example .env
    echo Por favor configura tu GEMINI_API_KEY en el archivo .env antes de analizar.
)

echo Iniciando la aplicacion en http://localhost:8501 ...
.\.venv\Scripts\python.exe -m streamlit run app\intermedio\cv_analyzer\app.py --server.port=8501
pause

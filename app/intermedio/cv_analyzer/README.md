# CV Analyzer

CV Analyzer extrae texto seleccionable de un currículum PDF y lo compara con una
vacante mediante Google Gemini. Devuelve un análisis Pydantic estructurado, un
porcentaje orientativo, una clasificación y una recomendación para revisión humana.

## Funcionalidades

- Validación en memoria de PDF, tamaño, integridad, páginas y texto extraíble.
- Vacante de hasta 10.000 caracteres con requisitos, habilidades y responsabilidades.
- Evaluación exclusiva con Google Gemini y salida nativa JSON Schema.
- Criterios fijos: experiencia 40 %, habilidades 35 %, formación 15 % y coherencia 10 %.
- Estado persistente durante la sesión, limpieza explícita y prevención de duplicados.
- Ejemplo reutilizable de vacante y descarga del análisis en formato JSON.
- Errores comprensibles sin puntuaciones ficticias ni exposición de secretos.
- Interfaz adaptable, contenedor no-root y healthcheck de Streamlit.

## Arquitectura

```text
app/intermedio/cv_analyzer/
├── app.py
├── models/cv_model.py
├── prompts/cv_prompts.py
├── services/
│   ├── config.py
│   ├── cv_evaluator.py
│   └── pdf_processor.py
└── ui/
    ├── presentation.py
    ├── streamlit_ui.py
    └── styles.css
```

El servicio de PDF trata el documento como entrada no confiable. El prompt separa el
contenido del CV y ordena ignorar instrucciones incrustadas. `cv_evaluator.py` usa
`ChatGoogleGenerativeAI.with_structured_output(..., method="json_schema")` y valida
el resultado con `AnalisisCV`.

## Requisitos y configuración

- Python 3.12.
- Una clave de [Google AI Studio](https://aistudio.google.com/app/apikey).
- Conexión a Internet durante las evaluaciones.
- Docker con Compose, opcional.

Copia `.env.example` como `.env` y configura:

```env
GEMINI_API_KEY=tu_clave
GEMINI_MODEL=gemini-3.5-flash
CV_MAX_FILE_SIZE_MB=10
CV_MAX_TEXT_CHARS=100000
```

`.env` está excluido de Git. La interfaz puede arrancar sin clave y solo exige una
al analizar. El modelo se puede cambiar mediante `GEMINI_MODEL` sin modificar código.

## Ejecución local

Desde la raíz del repositorio:

```bash
python -m venv .venv
# Windows: .\.venv\Scripts\Activate.ps1
# Linux/macOS: source .venv/bin/activate
python -m pip install -r requirements.txt
cd app/intermedio/cv_analyzer
python -m streamlit run app.py --server.port=8501
```

Abre <http://localhost:8501>.

## Docker Compose

```bash
docker compose up --build
```

Compose inicia directamente CV Analyzer en el puerto 8501. No requiere PostgreSQL,
pgAdmin ni volúmenes persistentes. Para comprobar la configuración sin iniciar:

```bash
docker compose config
```

## Pruebas y calidad

Las pruebas usan dobles de prueba para Gemini y no consumen cuota:

```bash
python -m pip install -r requirements-dev.txt
python -m pytest --cov=app/intermedio/cv_analyzer
python -m ruff check .
python -m compileall -q app tests
python -m pip check
```

Una prueba real de Gemini requiere una clave válida y consumo de cuota; no forma parte
de la suite ordinaria.

## Ejemplo de uso

1. Carga un PDF con texto seleccionable.
2. Describe la vacante, por ejemplo:

   ```text
   Puesto: Desarrollador Python.
   Experiencia: 3 años. Obligatorio: Python, REST y PostgreSQL.
   Deseable: Docker, pruebas automatizadas y LangChain.
   Responsabilidades: desarrollar servicios, integrar APIs y mantener pruebas.
   ```

3. Pulsa **Analizar Candidato** y revisa la evidencia, las brechas y la recomendación.

Un 65 % se muestra como **Bueno** y **Candidato con potencial**; son umbrales
independientes. La puntuación no reemplaza una decisión humana de contratación.

## Protección de datos y limitaciones

- El texto del CV y la vacante se envían a Google Gemini durante el análisis.
- La aplicación no persiste CV ni resultados y no registra el contenido completo.
- No se implementa OCR, procesamiento por lotes ni base de datos; Guardar descarga un
  JSON local, pero no persiste información en el servidor.
- Los resultados generativos pueden variar y deben revisarse por una persona.
- La evaluación excluye atributos personales irrelevantes y se limita a pertinencia
  profesional.

## Solución de problemas

| Síntoma | Revisión |
| --- | --- |
| Falta la clave | Define `GEMINI_API_KEY` en `.env` o en el entorno del proceso. |
| Modelo no disponible | Revisa `GEMINI_MODEL` y el acceso de la cuenta. |
| Cuota o límite | Espera y comprueba la cuota de Gemini; no hay reintentos indefinidos. |
| PDF sin texto | Usa un PDF con texto seleccionable; no se realiza OCR. |
| Puerto ocupado | Cambia el puerto local o el mapeo de Compose. |
| Docker no conecta | Inicia Docker Desktop o el daemon antes de `docker compose up`. |


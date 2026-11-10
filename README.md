# CV Analyzer

Aplicación web en Streamlit que compara un currículum en PDF con una descripción de
vacante mediante Google Gemini. El resultado incluye perfil profesional, experiencia,
habilidades, fortalezas, brechas, porcentaje de ajuste y una recomendación orientativa.

> La puntuación apoya la revisión humana. No constituye una decisión automática de
> contratación.

## Características

- Carga de currículums PDF con texto seleccionable, hasta 10 MB por defecto.
- Validación de archivos vacíos, dañados, cifrados o sin texto extraíble.
- Evaluación exclusiva con Google Gemini mediante `gemini-3.5-flash`.
- Respuesta estructurada con LangChain, JSON Schema y Pydantic.
- Protección del prompt frente a instrucciones incrustadas dentro del CV.
- Resultados persistentes durante la sesión con `st.session_state`.
- Botones para cargar una vacante de ejemplo, limpiar el formulario y reiniciar.
- Descarga local del análisis en JSON, sin base de datos ni persistencia en servidor.
- Manejo explícito de autenticación, cuota, timeout y saturación temporal 503.
- Docker Compose, healthcheck y ejecución como usuario no-root.
- Pruebas automatizadas sin consumir cuota real de Gemini.

## Flujo de análisis

1. El usuario carga un PDF con texto seleccionable.
2. Escribe los requisitos de la vacante o pulsa **Usar ejemplo**.
3. La aplicación valida el archivo y extrae su texto en memoria.
4. LangChain envía el CV y la vacante a Gemini como contenido no confiable delimitado.
5. Gemini genera un objeto compatible con `AnalisisCV`.
6. Pydantic valida todos los campos y el porcentaje entre 0 y 100.
7. Streamlit presenta el resultado y permite descargarlo como JSON.

Los CV y resultados no se guardan en una base de datos.

## Criterios de evaluación

| Criterio | Peso |
| --- | ---: |
| Experiencia relevante | 40 % |
| Habilidades técnicas | 35 % |
| Formación y certificaciones | 15 % |
| Coherencia profesional | 10 % |

Gemini estima el porcentaje siguiendo estos pesos. El código conserva dos conjuntos de
umbrales independientes:

| Porcentaje | Clasificación |
| --- | --- |
| 80–100 | Excelente |
| 60–79 | Bueno |
| 40–59 | Regular |
| 0–39 | Bajo |

| Porcentaje | Recomendación |
| --- | --- |
| 70–100 | Candidato recomendado |
| 50–69 | Candidato con potencial |
| 0–49 | Candidato no recomendado |

Por ejemplo, 65 % corresponde a **Bueno** y **Candidato con potencial**.

## Tecnologías

- Python 3.12
- Streamlit
- LangChain Core
- `langchain-google-genai`
- Google Gemini API
- Pydantic 2
- pypdf
- pytest y Ruff
- Docker y Docker Compose

## Estructura

```text
CV_Review/
├── app/intermedio/cv_analyzer/
│   ├── app.py
│   ├── models/
│   │   └── cv_model.py
│   ├── prompts/
│   │   └── cv_prompts.py
│   ├── services/
│   │   ├── config.py
│   │   ├── cv_evaluator.py
│   │   └── pdf_processor.py
│   └── ui/
│       ├── presentation.py
│       ├── streamlit_ui.py
│       └── styles.css
├── tests/
├── .env.example
├── compose.yaml
├── Dockerfile
├── requirements.txt
└── requirements-dev.txt
```

## Configuración

### 1. Crear el archivo de entorno

En Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

En Linux o macOS:

```bash
cp .env.example .env
```

Completa `.env`:

```env
GEMINI_API_KEY=tu_clave_de_google_ai_studio
GEMINI_MODEL=gemini-3.5-flash
CV_MAX_FILE_SIZE_MB=10
CV_MAX_TEXT_CHARS=100000
```

Puedes obtener una clave en [Google AI Studio](https://aistudio.google.com/app/apikey).
El archivo `.env` está ignorado por Git; nunca uses una clave real en `.env.example`.

### 2. Ejecución con Docker

Requiere Docker Desktop o un daemon compatible:

```bash
docker compose up --build -d
```

Abre <http://localhost:8501>.

Comandos útiles:

```bash
docker compose ps
docker compose logs -f cv-analyzer
docker compose down
```

El servicio debe aparecer como `healthy`. Si el puerto 8501 está ocupado, cambia el
mapeo en `compose.yaml`, por ejemplo a `8502:8501`.

### 3. Ejecución local

```bash
python -m venv .venv
```

Activa el entorno:

```powershell
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
```

```bash
# Linux o macOS
source .venv/bin/activate
```

Instala e inicia:

```bash
python -m pip install -r requirements.txt
cd app/intermedio/cv_analyzer
python -m streamlit run app.py --server.port=8501
```

## Uso

1. Abre la aplicación.
2. Carga un PDF de hasta 10 MB con texto seleccionable.
3. Describe el puesto, experiencia, habilidades, formación y responsabilidades.
4. Pulsa **Analizar Candidato**.
5. Revisa el porcentaje, clasificación, evidencia y recomendación.
6. Usa **Guardar análisis en JSON** si necesitas conservar el resultado localmente.
7. Usa **Limpiar** o **Limpiar análisis** para iniciar una evaluación nueva.

La aplicación no implementa OCR. Los PDF escaneados como imagen deben convertirse
previamente a un documento con texto seleccionable.

## Pruebas y calidad

Instala las dependencias de desarrollo:

```bash
python -m pip install -r requirements-dev.txt
```

Ejecuta las verificaciones:

```bash
python -m pytest
python -m pytest --cov=app/intermedio/cv_analyzer
python -m ruff check .
python -m compileall -q app tests
python -m pip check
docker compose config
```

Las pruebas de Gemini utilizan mocks. No requieren una clave ni consumen cuota.

## Seguridad y privacidad

- La clave se obtiene únicamente desde `GEMINI_API_KEY`.
- `.env`, entornos virtuales, cachés y artefactos locales están excluidos de Git.
- El contenido completo del CV no se escribe en logs.
- El PDF se procesa en memoria y no se guarda en el servidor.
- El prompt ignora instrucciones encontradas dentro del CV o la vacante.
- La evaluación excluye edad, género, nacionalidad, fotografía y otros atributos
  personales irrelevantes.
- El resultado debe ser revisado por una persona antes de tomar decisiones laborales.

El texto extraído del CV y la descripción de la vacante sí se envían a Google Gemini
para realizar el análisis.

## Solución de problemas

| Problema | Solución |
| --- | --- |
| `GEMINI_API_KEY` ausente | Crea `.env`, configura la clave y recrea el contenedor. |
| Error 401 o clave inválida | Genera una clave válida en Google AI Studio. |
| Error 429 | Revisa cuota y límites; espera antes de reintentar. |
| Error 503 por alta demanda | Gemini está temporalmente saturado. Espera unos segundos y vuelve a analizar. |
| Modelo sin acceso | Revisa `GEMINI_MODEL` y los permisos de la cuenta. |
| PDF sin texto | Usa un PDF con texto seleccionable; no hay OCR. |
| Límite incorrecto de carga | Verifica `CV_MAX_FILE_SIZE_MB` y recrea el contenedor. |
| `Connection lost` | Revisa `docker compose logs`; el contenedor configura un home escribible para Streamlit. |
| Puerto 8501 ocupado | Libera el puerto o cambia el mapeo del host en Compose. |

## Limitaciones

- Un CV por análisis.
- Sin OCR ni procesamiento por lotes.
- Sin historial persistente o base de datos.
- La exportación JSON se descarga en el navegador y no se guarda en el servidor.
- Los resultados generativos pueden variar incluso con la misma entrada.

La documentación específica del módulo está disponible en
[`app/intermedio/cv_analyzer/README.md`](app/intermedio/cv_analyzer/README.md).

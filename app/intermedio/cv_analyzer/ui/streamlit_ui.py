"""Streamlit workflow for uploading, evaluating, and presenting one CV."""

from __future__ import annotations

import hashlib
import logging
from pathlib import Path

import streamlit as st

from models.cv_model import AnalisisCV
from services.config import ErrorConfiguracionGemini, gemini_esta_configurado
from services.cv_evaluator import ErrorEvaluacionCV, evaluar_candidato
from services.pdf_processor import ErrorPDF, extraer_texto_pdf
from ui.presentation import (
    clasificar_ajuste,
    explicar_recomendacion,
    obtener_recomendacion,
)


logger = logging.getLogger(__name__)
RUTA_ESTILOS = Path(__file__).with_name("styles.css")


def inicializar_estado() -> None:
    """Create stable session keys without overwriting a previous result."""
    st.session_state.setdefault("analysis_result", None)
    st.session_state.setdefault("last_fingerprint", None)
    st.session_state.setdefault("analyzing", False)
    st.session_state.setdefault("uploader_version", 0)


def limpiar_analisis() -> None:
    """Reset inputs and result explicitly; a new uploader key clears its file."""
    st.session_state.analysis_result = None
    st.session_state.last_fingerprint = None
    st.session_state.analyzing = False
    st.session_state.uploader_version += 1
    st.session_state.pop("job_description", None)


def _huella(contenido: bytes, descripcion: str) -> str:
    digest = hashlib.sha256()
    digest.update(contenido)
    digest.update(descripcion.strip().encode("utf-8"))
    return digest.hexdigest()


def _mostrar_lista(titulo: str, elementos: list[str], vacio: str) -> None:
    st.subheader(titulo)
    if elementos:
        for elemento in elementos:
            st.markdown(f"- {elemento}")
    else:
        st.caption(vacio)


def mostrar_resultado(resultado: AnalisisCV) -> None:
    """Render the analysis independently from the button-click rerun."""
    porcentaje = resultado.porcentaje_ajuste
    clasificacion = clasificar_ajuste(porcentaje)
    recomendacion = obtener_recomendacion(porcentaje)

    st.divider()
    st.header("Resultado del análisis")
    metrica, categoria = st.columns(2)
    metrica.metric("Ajuste estimado", f"{porcentaje} %")
    categoria.metric("Clasificación", clasificacion)
    st.progress(porcentaje, text=f"Compatibilidad profesional orientativa: {porcentaje} %")

    st.subheader("Perfil del candidato")
    perfil, experiencia = st.columns(2)
    perfil.markdown(f"**Nombre:** {resultado.nombre_candidato}")
    perfil.markdown(f"**Educación:** {resultado.education}")
    experiencia.markdown(f"**Experiencia relevante:** {resultado.experiencia_años} años")
    experiencia.write(resultado.experiencia_relevante)

    habilidades, fortalezas, mejoras = st.columns(3)
    with habilidades:
        _mostrar_lista("Habilidades clave", resultado.habilidades_clave, "No disponibles")
    with fortalezas:
        _mostrar_lista("Fortalezas", resultado.fortalezas, "No identificadas")
    with mejoras:
        _mostrar_lista("Áreas de mejora", resultado.areas_mejora, "No identificadas")

    st.subheader("Recomendación final")
    st.info(
        explicar_recomendacion(porcentaje, resultado.fortalezas, resultado.areas_mejora)
    )
    st.caption(
        f"{recomendacion}. Esta puntuación es orientativa y apoya la revisión humana; "
        "no constituye una decisión automática de contratación."
    )
    if st.button("Guardar análisis", use_container_width=True):
        st.info("Guardar análisis es una funcionalidad prevista para una versión futura.")


def _procesar_analisis(archivo: object, descripcion: str) -> None:
    if archivo is None:
        st.error("Carga un currículum en formato PDF.")
        return
    if not descripcion.strip():
        st.error("Escribe la descripción de la vacante.")
        return

    nombre = str(getattr(archivo, "name", ""))
    if not nombre.lower().endswith(".pdf"):
        st.error("El archivo debe tener extensión .pdf.")
        return
    contenido = bytes(archivo.getvalue())
    huella = _huella(contenido, descripcion)
    if huella == st.session_state.last_fingerprint and st.session_state.analysis_result:
        st.info("Este CV ya fue analizado con la misma vacante; se conserva el resultado.")
        return

    st.session_state.analyzing = True
    try:
        with st.status("Analizando candidato con Gemini…", expanded=True) as estado:
            st.write("Validando y extrayendo texto del PDF…")
            texto = extraer_texto_pdf(contenido)
            st.write("Comparando evidencia profesional con la vacante…")
            resultado = evaluar_candidato(texto, descripcion)
            estado.update(label="Análisis completado", state="complete", expanded=False)
    except (ErrorPDF, ErrorConfiguracionGemini, ErrorEvaluacionCV, ValueError) as exc:
        st.error(str(exc))
    except Exception as exc:  # Defensive UI boundary; details stay in technical logs.
        logger.error("Unexpected analysis UI error: %s", type(exc).__name__, exc_info=True)
        st.error("Ocurrió un error inesperado. Revisa los logs técnicos e inténtalo de nuevo.")
    else:
        st.session_state.analysis_result = resultado
        st.session_state.last_fingerprint = huella
    finally:
        st.session_state.analyzing = False


def main() -> None:
    """Configure and run the complete CV Analyzer interface."""
    st.set_page_config(page_title="CV Analyzer", page_icon="📄", layout="wide")
    st.markdown(
        f"<style>{RUTA_ESTILOS.read_text(encoding='utf-8')}</style>",
        unsafe_allow_html=True,
    )
    inicializar_estado()

    titulo, acciones = st.columns([4, 1])
    with titulo:
        st.title("CV Analyzer")
        st.write("Compara un currículum con una vacante mediante Google Gemini.")
    with acciones:
        st.button(
            "Limpiar",
            on_click=limpiar_analisis,
            use_container_width=True,
            disabled=st.session_state.analyzing,
        )

    if gemini_esta_configurado():
        st.success("Gemini configurado", icon="✅")
    else:
        st.warning(
            "La interfaz está disponible, pero debes configurar GEMINI_API_KEY para analizar.",
            icon="⚙️",
        )
    st.info(
        "Al analizar, el texto extraído del CV y la descripción se envían a Google Gemini. "
        "No se almacenan en una base de datos.",
        icon="🔐",
    )

    with st.form("analysis_form"):
        archivo = st.file_uploader(
            "Currículum en PDF",
            type=["pdf"],
            key=f"cv_pdf_{st.session_state.uploader_version}",
            help="PDF con texto seleccionable. Tamaño predeterminado máximo: 10 MB.",
        )
        descripcion = st.text_area(
            "Descripción de la vacante",
            key="job_description",
            height=220,
            max_chars=10_000,
            placeholder=(
                "Puesto, experiencia requerida, habilidades obligatorias y deseables, "
                "formación y responsabilidades…"
            ),
        )
        analizar = st.form_submit_button(
            "Analizar Candidato",
            type="primary",
            use_container_width=True,
            disabled=st.session_state.analyzing,
        )

    if analizar:
        _procesar_analisis(archivo, descripcion)
    if st.session_state.analysis_result is not None:
        mostrar_resultado(st.session_state.analysis_result)


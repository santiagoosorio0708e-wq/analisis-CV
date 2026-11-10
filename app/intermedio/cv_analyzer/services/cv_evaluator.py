"""Gemini-backed CV evaluation with structured output and safe failures."""

from __future__ import annotations

import logging
from typing import Any

from langchain_core.exceptions import OutputParserException
from langchain_core.runnables import Runnable
from langchain_google_genai import ChatGoogleGenerativeAI
from models.cv_model import AnalisisCV
from prompts.cv_prompts import crear_sistema_prompts
from pydantic import ValidationError
from services.config import ConfiguracionGemini, cargar_configuracion_gemini

logger = logging.getLogger(__name__)


class ErrorEvaluacionCV(RuntimeError):
    """A safe, user-facing Gemini evaluation error."""


class RespuestaGeminiInvalidaError(ErrorEvaluacionCV):
    """Gemini returned no valid AnalisisCV object."""


def crear_evaluador_cv(
    configuracion: ConfiguracionGemini | None = None,
) -> Runnable[Any, AnalisisCV]:
    """Create a LangChain pipeline using Gemini native JSON Schema output."""
    config = configuracion or cargar_configuracion_gemini()
    modelo = ChatGoogleGenerativeAI(
        model=config.model,
        api_key=config.api_key,
        max_retries=1,
        timeout=60,
    )
    estructurado = modelo.with_structured_output(
        AnalisisCV,
        method="json_schema",
    )
    return crear_sistema_prompts() | estructurado


def _mensaje_error_gemini(exc: Exception) -> str:
    nombre = type(exc).__name__.lower()
    mensaje = str(exc).lower()
    detalle = f"{nombre} {mensaje}"
    if any(valor in detalle for valor in ("authentication", "unauthenticated", "api key")):
        return "La clave de Gemini no es válida. Revisa GEMINI_API_KEY."
    if any(valor in detalle for valor in ("permission", "forbidden")):
        return "La clave no tiene acceso al modelo Gemini configurado."
    if any(valor in detalle for valor in ("notfound", "not found", "modelnotfound")):
        return "El modelo configurado no existe o no está disponible para esta cuenta."
    if any(valor in detalle for valor in ("ratelimit", "resourceexhausted", "quota", "429")):
        return "Gemini alcanzó un límite de solicitudes o cuota. Inténtalo más tarde."
    if any(valor in detalle for valor in ("timeout", "deadline")):
        return "Gemini tardó demasiado en responder. Inténtalo nuevamente."
    if any(valor in detalle for valor in ("connection", "network", "unavailable", "503")):
        return "No fue posible conectar con Gemini. Revisa la conexión e inténtalo de nuevo."
    return "Gemini no pudo completar el análisis. Inténtalo nuevamente más tarde."


def evaluar_candidato(
    cv_texto: str,
    descripcion_vacante: str,
    *,
    evaluador: Runnable[Any, AnalisisCV] | None = None,
) -> AnalisisCV:
    """Evaluate validated inputs; never fabricate a fallback score on failure."""
    if not cv_texto.strip():
        raise ValueError("El texto del CV no puede estar vacío.")
    if not descripcion_vacante.strip():
        raise ValueError("La descripción de la vacante no puede estar vacía.")

    cadena = evaluador or crear_evaluador_cv()
    try:
        resultado = cadena.invoke(
            {
                "cv_texto": cv_texto,
                "descripcion_vacante": descripcion_vacante,
            }
        )
    except (ValidationError, OutputParserException) as exc:
        logger.warning("Gemini returned an invalid structured response: %s", type(exc).__name__)
        raise RespuestaGeminiInvalidaError(
            "Gemini devolvió una respuesta incompatible con el formato esperado."
        ) from exc
    except ErrorEvaluacionCV:
        raise
    except Exception as exc:
        logger.error("Gemini evaluation failed: %s", type(exc).__name__, exc_info=True)
        raise ErrorEvaluacionCV(_mensaje_error_gemini(exc)) from exc

    if resultado is None:
        raise RespuestaGeminiInvalidaError("Gemini devolvió una respuesta vacía.")
    if isinstance(resultado, dict):
        try:
            resultado = AnalisisCV.model_validate(resultado)
        except ValidationError as exc:
            raise RespuestaGeminiInvalidaError(
                "Gemini devolvió una respuesta incompatible con el formato esperado."
            ) from exc
    if not isinstance(resultado, AnalisisCV):
        raise RespuestaGeminiInvalidaError(
            "Gemini devolvió una respuesta incompatible con el formato esperado."
        )
    return resultado

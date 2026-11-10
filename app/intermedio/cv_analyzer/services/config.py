"""Environment-backed configuration without secret exposure."""

import os
from dataclasses import dataclass

from dotenv import load_dotenv
from pydantic import SecretStr

DEFAULT_GEMINI_MODEL = "gemini-3.5-flash"
PLACEHOLDER_KEYS = {"", "tu_clave_de_gemini", "your_gemini_api_key"}


class ErrorConfiguracionGemini(RuntimeError):
    """Gemini cannot be called with the current environment."""


@dataclass(frozen=True)
class ConfiguracionGemini:
    api_key: SecretStr
    model: str


def cargar_configuracion_gemini() -> ConfiguracionGemini:
    """Load and validate Gemini settings only when an analysis is requested."""
    load_dotenv()
    clave = os.getenv("GEMINI_API_KEY", "").strip()
    modelo = os.getenv("GEMINI_MODEL", DEFAULT_GEMINI_MODEL).strip()
    if clave.lower() in PLACEHOLDER_KEYS:
        raise ErrorConfiguracionGemini(
            "Configura GEMINI_API_KEY en el entorno o en un archivo .env local."
        )
    if not modelo:
        raise ErrorConfiguracionGemini("GEMINI_MODEL no puede estar vacío.")
    return ConfiguracionGemini(api_key=SecretStr(clave), model=modelo)


def gemini_esta_configurado() -> bool:
    """Report availability without creating a client or revealing the key."""
    try:
        cargar_configuracion_gemini()
    except ErrorConfiguracionGemini:
        return False
    return True

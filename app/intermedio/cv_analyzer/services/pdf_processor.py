"""Safe, in-memory PDF validation and text extraction."""

from __future__ import annotations

import os
from io import BytesIO
from typing import BinaryIO

from pypdf import PdfReader
from pypdf.errors import PdfReadError

DEFAULT_MAX_FILE_SIZE_MB = 10
DEFAULT_MAX_TEXT_CHARS = 100_000


class ErrorPDF(ValueError):
    """Base error for user-correctable PDF problems."""


class PDFVacioError(ErrorPDF):
    """The uploaded file has no bytes or no pages."""


class PDFDanadoError(ErrorPDF):
    """The uploaded bytes do not form a readable PDF."""


class PDFSinTextoError(ErrorPDF):
    """The PDF is readable but contains no selectable text."""


class PDFDemasiadoGrandeError(ErrorPDF):
    """The upload or extracted text exceeds the configured bound."""


def _entero_entorno(nombre: str, predeterminado: int) -> int:
    try:
        valor = int(os.getenv(nombre, str(predeterminado)))
    except ValueError:
        return predeterminado
    return valor if valor > 0 else predeterminado


def _leer_bytes(archivo: bytes | BinaryIO) -> bytes:
    if isinstance(archivo, bytes):
        return archivo
    if hasattr(archivo, "getvalue"):
        return bytes(archivo.getvalue())
    posicion = archivo.tell() if hasattr(archivo, "tell") else None
    contenido = archivo.read()
    if posicion is not None and hasattr(archivo, "seek"):
        archivo.seek(posicion)
    return contenido


def extraer_texto_pdf(
    archivo: bytes | BinaryIO,
    *,
    max_file_size_mb: int | None = None,
    max_text_chars: int | None = None,
) -> str:
    """Validate a PDF and extract selectable text from all pages in memory."""
    limite_mb = max_file_size_mb or _entero_entorno("CV_MAX_FILE_SIZE_MB", DEFAULT_MAX_FILE_SIZE_MB)
    limite_texto = max_text_chars or _entero_entorno("CV_MAX_TEXT_CHARS", DEFAULT_MAX_TEXT_CHARS)
    contenido = _leer_bytes(archivo)

    if not contenido:
        raise PDFVacioError("El archivo PDF está vacío.")
    if len(contenido) > limite_mb * 1024 * 1024:
        raise PDFDemasiadoGrandeError(f"El PDF supera el límite configurado de {limite_mb} MB.")
    if not contenido.startswith(b"%PDF-"):
        raise PDFDanadoError("El archivo no tiene un encabezado PDF válido.")

    try:
        lector = PdfReader(BytesIO(contenido), strict=False)
        if lector.is_encrypted and not lector.decrypt(""):
            raise PDFDanadoError("El PDF está protegido con contraseña.")
        if not lector.pages:
            raise PDFVacioError("El PDF no contiene páginas.")
        paginas = [(pagina.extract_text() or "").strip() for pagina in lector.pages]
    except ErrorPDF:
        raise
    except (PdfReadError, OSError, ValueError, TypeError) as exc:
        raise PDFDanadoError("No fue posible leer el PDF; puede estar dañado.") from exc

    texto = "\n\n--- Página siguiente ---\n\n".join(pagina for pagina in paginas if pagina).strip()
    if not texto:
        raise PDFSinTextoError(
            "El PDF no contiene texto seleccionable. La aplicación no realiza OCR."
        )
    if len(texto) > limite_texto:
        raise PDFDemasiadoGrandeError(
            f"El texto extraído supera el límite de {limite_texto:,} caracteres."
        )
    return texto

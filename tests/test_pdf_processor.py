from io import BytesIO

import pytest
from pypdf import PdfWriter
from services.pdf_processor import (
    PDFDanadoError,
    PDFDemasiadoGrandeError,
    PDFSinTextoError,
    PDFVacioError,
    extraer_texto_pdf,
    obtener_limite_archivo_mb,
)


def crear_pdf_con_texto(texto: str) -> bytes:
    """Create a small standards-compliant text PDF without test-only packages."""
    flujo = f"BT /F1 12 Tf 72 720 Td ({texto}) Tj ET".encode("ascii")
    objetos = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        (
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            b"/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>"
        ),
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length " + str(len(flujo)).encode() + b" >>\nstream\n" + flujo + b"\nendstream",
    ]
    documento = bytearray(b"%PDF-1.4\n")
    posiciones = [0]
    for indice, objeto in enumerate(objetos, start=1):
        posiciones.append(len(documento))
        documento.extend(f"{indice} 0 obj\n".encode())
        documento.extend(objeto + b"\nendobj\n")
    inicio_xref = len(documento)
    documento.extend(f"xref\n0 {len(objetos) + 1}\n".encode())
    documento.extend(b"0000000000 65535 f \n")
    for posicion in posiciones[1:]:
        documento.extend(f"{posicion:010d} 00000 n \n".encode())
    documento.extend(
        f"trailer\n<< /Size {len(objetos) + 1} /Root 1 0 R >>\n"
        f"startxref\n{inicio_xref}\n%%EOF\n".encode()
    )
    return bytes(documento)


def crear_pdf_sin_texto() -> bytes:
    salida = BytesIO()
    escritor = PdfWriter()
    escritor.add_blank_page(width=612, height=792)
    escritor.write(salida)
    return salida.getvalue()


def test_pdf_valido_con_texto_extraible():
    assert "Jane Doe" in extraer_texto_pdf(crear_pdf_con_texto("Jane Doe"))


def test_pdf_vacio():
    with pytest.raises(PDFVacioError):
        extraer_texto_pdf(b"")


def test_pdf_danado():
    with pytest.raises(PDFDanadoError):
        extraer_texto_pdf(b"%PDF-1.4\ncontenido roto")


def test_pdf_sin_texto_seleccionable():
    with pytest.raises(PDFSinTextoError):
        extraer_texto_pdf(crear_pdf_sin_texto())


def test_pdf_supera_limite():
    with pytest.raises(PDFDemasiadoGrandeError):
        extraer_texto_pdf(crear_pdf_con_texto("Jane Doe"), max_file_size_mb=0.0001)


def test_limite_archivo_se_obtiene_del_entorno(monkeypatch):
    monkeypatch.setenv("CV_MAX_FILE_SIZE_MB", "12")
    assert obtener_limite_archivo_mb() == 12

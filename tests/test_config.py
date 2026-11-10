import pytest
from services.config import ErrorConfiguracionGemini, cargar_configuracion_gemini


def test_clave_api_ausente(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    # An explicit empty value prevents python-dotenv from loading a developer key.
    monkeypatch.setenv("GEMINI_API_KEY", "")
    with pytest.raises(ErrorConfiguracionGemini, match="GEMINI_API_KEY"):
        cargar_configuracion_gemini()


def test_modelo_predeterminado(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("GEMINI_API_KEY", "clave-prueba-no-real")
    monkeypatch.delenv("GEMINI_MODEL", raising=False)
    assert cargar_configuracion_gemini().model == "gemini-3.5-flash"

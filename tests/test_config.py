import pytest

from services.config import ErrorConfiguracionGemini, cargar_configuracion_gemini


def test_clave_api_ausente(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    with pytest.raises(ErrorConfiguracionGemini, match="GEMINI_API_KEY"):
        cargar_configuracion_gemini()


def test_modelo_predeterminado(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("GEMINI_API_KEY", "clave-prueba-no-real")
    monkeypatch.delenv("GEMINI_MODEL", raising=False)
    assert cargar_configuracion_gemini().model == "gemini-3.5-flash"


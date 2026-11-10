from ui import streamlit_ui


class Estado(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__


def test_limpiar_analisis_restablece_estado(monkeypatch):
    estado = Estado(
        analysis_result=object(),
        last_fingerprint="abc",
        analyzing=True,
        uploader_version=2,
        job_description="Vacante",
    )
    monkeypatch.setattr(streamlit_ui.st, "session_state", estado)
    streamlit_ui.limpiar_analisis()
    assert estado["analysis_result"] is None
    assert estado["last_fingerprint"] is None
    assert estado["analyzing"] is False
    assert estado["uploader_version"] == 3
    assert "job_description" not in estado

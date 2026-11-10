import pytest
from models.cv_model import AnalisisCV
from services.cv_evaluator import (
    ErrorEvaluacionCV,
    RespuestaGeminiInvalidaError,
    evaluar_candidato,
)
from ui.streamlit_ui import crear_json_analisis


class EvaluadorSimulado:
    def __init__(self, resultado=None, error=None):
        self.resultado = resultado
        self.error = error
        self.entrada = None

    def invoke(self, entrada):
        self.entrada = entrada
        if self.error:
            raise self.error
        return self.resultado


def analisis_valido():
    return AnalisisCV(
        nombre_candidato="Grace Hopper",
        experiencia_años=8,
        habilidades_clave=["Python"],
        education="Matemáticas",
        experiencia_relevante="Ingeniería de software",
        fortalezas=["Experiencia"],
        areas_mejora=["No disponible en el CV"],
        porcentaje_ajuste=85,
    )


def test_flujo_exitoso_con_gemini_simulado():
    simulado = EvaluadorSimulado(analisis_valido())
    resultado = evaluar_candidato("CV", "Vacante", evaluador=simulado)
    assert resultado.porcentaje_ajuste == 85
    assert simulado.entrada == {"cv_texto": "CV", "descripcion_vacante": "Vacante"}


def test_descripcion_vacia():
    with pytest.raises(ValueError, match="vacante"):
        evaluar_candidato("CV", "  ", evaluador=EvaluadorSimulado())


def test_respuesta_invalida_de_gemini():
    with pytest.raises(RespuestaGeminiInvalidaError):
        evaluar_candidato(
            "CV",
            "Vacante",
            evaluador=EvaluadorSimulado({"porcentaje_ajuste": 500}),
        )


def test_respuesta_vacia_de_gemini():
    with pytest.raises(RespuestaGeminiInvalidaError, match="vacía"):
        evaluar_candidato("CV", "Vacante", evaluador=EvaluadorSimulado(None))


def test_excepcion_de_api_se_convierte_en_error_seguro():
    simulado = EvaluadorSimulado(error=TimeoutError("deadline exceeded"))
    with pytest.raises(ErrorEvaluacionCV, match="tardó demasiado"):
        evaluar_candidato("CV", "Vacante", evaluador=simulado)


def test_saturacion_temporal_de_gemini_tiene_mensaje_especifico():
    simulado = EvaluadorSimulado(
        error=RuntimeError("503 UNAVAILABLE: model is experiencing high demand")
    )
    with pytest.raises(ErrorEvaluacionCV, match="temporalmente saturado"):
        evaluar_candidato("CV", "Vacante", evaluador=simulado)


def test_exportacion_json_incluye_clasificacion_y_recomendacion():
    contenido = crear_json_analisis(analisis_valido())
    assert '"clasificacion": "Excelente"' in contenido
    assert '"recomendacion": "Candidato recomendado"' in contenido

import pytest
from pydantic import ValidationError

from models.cv_model import AnalisisCV
from ui.presentation import clasificar_ajuste, obtener_recomendacion


def datos_validos(**cambios):
    datos = {
        "nombre_candidato": "Ada Lovelace",
        "experiencia_años": 4,
        "habilidades_clave": ["Python"],
        "education": "Matemáticas",
        "experiencia_relevante": "Desarrollo analítico",
        "fortalezas": ["Razonamiento"],
        "areas_mejora": ["Docker"],
        "porcentaje_ajuste": 80,
    }
    datos.update(cambios)
    return datos


def test_analisis_cv_valido():
    resultado = AnalisisCV(**datos_validos())
    assert resultado.porcentaje_ajuste == 80
    assert resultado.nombre_candidato == "Ada Lovelace"


@pytest.mark.parametrize("porcentaje", [-1, 101])
def test_porcentaje_fuera_de_rango(porcentaje):
    with pytest.raises(ValidationError):
        AnalisisCV(**datos_validos(porcentaje_ajuste=porcentaje))


@pytest.mark.parametrize(
    ("porcentaje", "esperado"),
    [(39, "Bajo"), (40, "Regular"), (59, "Regular"), (60, "Bueno"), (79, "Bueno"), (80, "Excelente")],
)
def test_limites_clasificacion(porcentaje, esperado):
    assert clasificar_ajuste(porcentaje) == esperado


@pytest.mark.parametrize(
    ("porcentaje", "esperado"),
    [
        (49, "Candidato no recomendado"),
        (50, "Candidato con potencial"),
        (69, "Candidato con potencial"),
        (70, "Candidato recomendado"),
    ],
)
def test_limites_recomendacion(porcentaje, esperado):
    assert obtener_recomendacion(porcentaje) == esperado


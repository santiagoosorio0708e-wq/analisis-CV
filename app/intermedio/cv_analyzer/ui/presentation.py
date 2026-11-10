"""Deterministic labels that remain separate from Gemini's score estimate."""


def clasificar_ajuste(porcentaje: int) -> str:
    """Map the score to the workshop's main classification thresholds."""
    if not 0 <= porcentaje <= 100:
        raise ValueError("El porcentaje debe estar entre 0 y 100.")
    if porcentaje >= 80:
        return "Excelente"
    if porcentaje >= 60:
        return "Bueno"
    if porcentaje >= 40:
        return "Regular"
    return "Bajo"


def obtener_recomendacion(porcentaje: int) -> str:
    """Map the score to the independent recommendation thresholds."""
    if not 0 <= porcentaje <= 100:
        raise ValueError("El porcentaje debe estar entre 0 y 100.")
    if porcentaje >= 70:
        return "Candidato recomendado"
    if porcentaje >= 50:
        return "Candidato con potencial"
    return "Candidato no recomendado"


def explicar_recomendacion(
    porcentaje: int,
    fortalezas: list[str],
    areas_mejora: list[str],
) -> str:
    """Build a brief evidence-based explanation without adding candidate facts."""
    recomendacion = obtener_recomendacion(porcentaje)
    fortaleza = fortalezas[0] if fortalezas else "sin fortalezas verificables destacadas"
    brecha = areas_mejora[0] if areas_mejora else "sin brechas críticas identificadas"
    return f"{recomendacion}: {fortaleza}; {brecha}."


"""Structured result returned by Gemini for a CV evaluation."""

from pydantic import BaseModel, ConfigDict, Field, field_validator


class AnalisisCV(BaseModel):
    """Professional fit analysis with the contract defined by the workshop."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    nombre_candidato: str = Field(min_length=1, description="Nombre indicado en el CV")
    experiencia_años: int = Field(ge=0, description="Años de experiencia relevante")
    habilidades_clave: list[str] = Field(description="Habilidades relevantes verificables")
    education: str = Field(min_length=1, description="Formación indicada en el CV")
    experiencia_relevante: str = Field(
        min_length=1,
        description="Resumen de experiencia relacionada con la vacante",
    )
    fortalezas: list[str] = Field(description="Fortalezas profesionales verificables")
    areas_mejora: list[str] = Field(description="Brechas frente a la vacante")
    porcentaje_ajuste: int = Field(ge=0, le=100, description="Ajuste profesional orientativo")

    @field_validator("habilidades_clave", "fortalezas", "areas_mejora")
    @classmethod
    def validar_listas(cls, valores: list[str]) -> list[str]:
        """Reject empty items while preserving intentionally empty lists."""
        limpios = [valor.strip() for valor in valores]
        if any(not valor for valor in limpios):
            raise ValueError("los elementos no pueden estar vacíos")
        return limpios


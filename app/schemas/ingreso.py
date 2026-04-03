from datetime import date

from pydantic import BaseModel, field_validator


class IngresoDiarioResponse(BaseModel):
    recibo: int
    fecha: date
    total: float
    fpago: str
    cliente: str
    descrip: str
    usuario: str

    @field_validator("total", mode="before")
    @classmethod
    def format_total(cls, v):
        if isinstance(v, (int, float)):
            return float(f"{v:.2f}")
        return v

    class Config:
        from_attributes = True


class ResumenDiaItem(BaseModel):
    descrip: str
    total_recibos: int
    total: float

    @field_validator("total", mode="before")
    @classmethod
    def format_total(cls, v):
        if isinstance(v, (int, float)):
            return float(f"{v:.2f}")
        return v


class ResumenDiaResponse(BaseModel):
    fecha_inicio: date
    fecha_fin: date
    data: list[ResumenDiaItem]


class IngresoRangoResponse(BaseModel):
    fecha_inicio: date
    fecha_fin: date
    total: float


class GraficaDataPoint(BaseModel):
    fecha: date
    monto: float


class IngresoGraficaResponse(BaseModel):
    data: list[GraficaDataPoint]

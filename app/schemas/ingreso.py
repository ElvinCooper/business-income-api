from datetime import date
from typing import Annotated

from pydantic import BaseModel, Field


class IngresoDiarioBase(BaseModel):
    fecha: date
    monto: float = Field(gt=0)


class IngresoDiarioCreate(IngresoDiarioBase):
    pass


class IngresoDiarioResponse(IngresoDiarioBase):
    id: int

    class Config:
        from_attributes = True


class IngresoRangoResponse(BaseModel):
    fecha_inicio: date
    fecha_fin: date
    total: float


class GraficaDataPoint(BaseModel):
    fecha: date
    monto: float


class IngresoGraficaResponse(BaseModel):
    data: list[GraficaDataPoint]

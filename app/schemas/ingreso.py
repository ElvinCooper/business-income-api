from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator, field_serializer


def _to_float(v):
    if isinstance(v, (int, float, Decimal)):
        return round(float(v), 2)
    return v


class IngresoDiarioResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    recibo: int
    fecha: date
    total: Decimal = Field(max_digits=15, decimal_places=2)
    fpago: str
    cliente: str
    descrip: str
    usuario: str

    @field_validator("total", mode="before")
    @classmethod
    def format_total(cls, v):
        return _to_float(v)

    @field_serializer("total")
    def serialize_total(self, v: Decimal) -> float:
        return round(float(v), 2)


class IngresoDiarioWrapper(BaseModel):
    data: list[IngresoDiarioResponse]
    total_general: Decimal = Field(max_digits=15, decimal_places=2)

    @field_validator("total_general", mode="before")
    @classmethod
    def format_total_general(cls, v):
        return _to_float(v)

    @field_serializer("total_general")
    def serialize_total_general(self, v: Decimal) -> float:
        return round(float(v), 2)


class ResumenDiaItem(BaseModel):
    fecha: date
    descrip: str
    total_recibos: int
    total: Decimal = Field(max_digits=15, decimal_places=2)

    @field_validator("total", mode="before")
    @classmethod
    def format_total(cls, v):
        return _to_float(v)

    @field_serializer("total")
    def serialize_total(self, v: Decimal) -> float:
        return round(float(v), 2)


class ResumenDiaResponse(BaseModel):
    fecha_inicio: date
    fecha_fin: date
    data: list[ResumenDiaItem]
    total_general: Decimal = Field(max_digits=15, decimal_places=2)

    @field_validator("total_general", mode="before")
    @classmethod
    def format_total_general(cls, v):
        return _to_float(v)

    @field_serializer("total_general")
    def serialize_total_general(self, v: Decimal) -> float:
        return round(float(v), 2)


class IngresoRangoResponse(BaseModel):
    fecha_inicio: date
    fecha_fin: date
    total: Decimal = Field(max_digits=15, decimal_places=2)

    @field_validator("total", mode="before")
    @classmethod
    def format_total(cls, v):
        return _to_float(v)

    @field_serializer("total")
    def serialize_total(self, v: Decimal) -> float:
        return round(float(v), 2)


class GraficaDataPoint(BaseModel):
    fecha: date
    monto: Decimal = Field(max_digits=15, decimal_places=2)

    @field_validator("monto", mode="before")
    @classmethod
    def format_monto(cls, v):
        return _to_float(v)

    @field_serializer("monto")
    def serialize_monto(self, v: Decimal) -> float:
        return round(float(v), 2)


class IngresoGraficaResponse(BaseModel):
    data: list[GraficaDataPoint]


class IngresoMensualItem(BaseModel):
    mes: int
    total_recibos: int
    total: Decimal = Field(max_digits=15, decimal_places=2)

    @field_validator("total", mode="before")
    @classmethod
    def format_total(cls, v):
        return _to_float(v)

    @field_serializer("total")
    def serialize_total(self, v: Decimal) -> float:
        return round(float(v), 2)


class IngresoAnualResponse(BaseModel):
    year: int
    data: list[IngresoMensualItem]
    total_general: Decimal = Field(max_digits=15, decimal_places=2)

    @field_validator("total_general", mode="before")
    @classmethod
    def format_total_general(cls, v):
        return _to_float(v)

    @field_serializer("total_general")
    def serialize_total_general(self, v: Decimal) -> float:
        return round(float(v), 2)


class ResumenUsuarioItem(BaseModel):
    usuario: str
    total_recibos: int
    total: Decimal = Field(max_digits=15, decimal_places=2)

    @field_validator("total", mode="before")
    @classmethod
    def format_total(cls, v):
        return _to_float(v)

    @field_serializer("total")
    def serialize_total(self, v: Decimal) -> float:
        return round(float(v), 2)


class ResumenUsuarioResponse(BaseModel):
    fecha_inicio: date
    fecha_fin: date
    data: list[ResumenUsuarioItem]
    total_general: Decimal = Field(max_digits=15, decimal_places=2)

    @field_validator("total_general", mode="before")
    @classmethod
    def format_total_general(cls, v):
        return _to_float(v)

    @field_serializer("total_general")
    def serialize_total_general(self, v: Decimal) -> float:
        return round(float(v), 2)

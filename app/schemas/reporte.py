from pydantic import BaseModel, Field


class ReporteItem(BaseModel):
    descripcion: str
    valor: float = Field(ge=0)


class ReportePago(BaseModel):
    tipo: str
    valor: float = Field(ge=0)


class ReporteVentasRequest(BaseModel):
    empresa: str
    direccion: str
    telefono: str
    rnc: str
    desde: str
    hasta: str
    fecha_impresion: str
    usuario: str
    items: list[ReporteItem]
    total: float = Field(ge=0)
    pagos: list[ReportePago]

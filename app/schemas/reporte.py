from pydantic import BaseModel, Field


class ReciboPago(BaseModel):
    idnum: int = Field(description="Número único de pago/recibo")
    cliente: str = Field(description="Nombre del cliente")
    monto: float = Field(ge=0, description="Monto pagado")


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

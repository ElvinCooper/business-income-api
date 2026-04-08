from datetime import date
from typing import Annotated

from pydantic import BaseModel, Field


class ReciboPago(BaseModel):
    idnum: int = Field(description="Número único de pago/recibo")
    cliente: str = Field(description="Nombre del cliente")
    monto: float = Field(ge=0, description="Monto pagado")


class ReporteVentasRequest(BaseModel):
    desde: Annotated[date, Field(description="Fecha inicio YYYY-MM-DD")]
    hasta: Annotated[date, Field(description="Fecha fin YYYY-MM-DD")]
    metodos_pago: Annotated[
        list[str] | None,
        Field(description="Lista de formas de pago a incluir (opcional)"),
    ] = None

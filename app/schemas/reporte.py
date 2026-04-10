from datetime import date
from typing import Annotated

from pydantic import BaseModel, Field


class ReciboPago(BaseModel):
    recibo: int = Field(description="Número único de recibo")
    cliente: str = Field(description="Nombre del cliente")
    monto: float = Field(ge=0, description="Monto pagado")
    #metodo_pago: str = Field(examples="Efectivo, Tarjeta, Transferencia, Cheque")


class ReporteVentasRequest(BaseModel):
    desde: Annotated[date, Field(description="Fecha inicio YYYY-MM-DD")]
    hasta: Annotated[date, Field(description="Fecha fin YYYY-MM-DD")]

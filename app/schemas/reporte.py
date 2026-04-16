from datetime import date
from typing import Annotated

from pydantic import BaseModel, Field


class ReciboPago(BaseModel):
    model_config = {
        "json_schema_extra": {
            "examples": [
                {"recibo": 1001, "cliente": "Juan Pérez", "monto": 1500.00},
                {"recibo": 1002, "cliente": "María López", "monto": 2500.50},
            ]
        }
    }

    recibo: int = Field(description="Número único de recibo")
    cliente: str = Field(description="Nombre del cliente")
    monto: float = Field(ge=0, description="Monto pagado")


class ReporteVentasRequest(BaseModel):
    model_config = {
        "json_schema_extra": {
            "examples": [
                {"desde": "2025-04-01", "hasta": "2025-04-15"},
                {"desde": "2025-01-01", "hasta": "2025-03-31"},
            ]
        }
    }

    desde: Annotated[date, Field(description="Fecha inicio YYYY-MM-DD")]
    hasta: Annotated[date, Field(description="Fecha fin YYYY-MM-DD")]

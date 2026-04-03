from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.core.dependencies import CurrentUserDep
from app.db.connection import DatabaseConnection, get_db
from app.schemas.ingreso import IngresoRangoResponse

router = APIRouter(prefix="/ingresos", tags=["ingresos"])


@router.get("/rango", response_model=IngresoRangoResponse)
async def get_ingresos_rango(
    fecha_inicio: Annotated[date, Query(description="Fecha inicio YYYY-MM-DD")],
    fecha_fin: Annotated[date, Query(description="Fecha fin YYYY-MM-DD")],
    current_user: CurrentUserDep,
    db: Annotated[DatabaseConnection, Depends(get_db)],
):
    """Obtiene el total de ingresos en un rango de fechas."""
    pass

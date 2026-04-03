from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.core.dependencies import CurrentUserDep
from app.db.connection import DatabaseConnection, get_db
from app.schemas.ingreso import IngresoDiarioResponse

router = APIRouter(prefix="/ingresos", tags=["ingresos"])


@router.get("/diarios", response_model=IngresoDiarioResponse | None)
async def get_ingresos_diarios(
    fecha: Annotated[date, Query(description="Fecha en formato YYYY-MM-DD")],
    current_user: CurrentUserDep,
    db: Annotated[DatabaseConnection, Depends(get_db)],
):
    """Obtiene los ingresos de un día específico."""
    pass


@router.post("/diarios", response_model=IngresoDiarioResponse)
async def create_ingreso_diario(
    ingreso: IngresoDiarioResponse,
    current_user: CurrentUserDep,
    db: Annotated[DatabaseConnection, Depends(get_db)],
):
    """Registra los ingresos de un día."""
    pass

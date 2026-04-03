from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.core.dependencies import CurrentUserDep
from app.db.connection import DatabaseConnection, get_db
from app.schemas.ingreso import IngresoDiarioResponse, ResumenDiaResponse

router = APIRouter(prefix="/ingresos", tags=["ingresos"])


@router.get("/diarios", response_model=list[IngresoDiarioResponse])
async def get_ingresos_diarios(
    fecha: Annotated[date, Query(description="Fecha en formato YYYY-MM-DD")],
    current_user: CurrentUserDep,
    db: Annotated[DatabaseConnection, Depends(get_db)],
):
    """Obtiene los ingresos de un día específico."""
    query = """
        SELECT recibo, fecha, total, fpago, cliente, descrip, usuario
        FROM cxc
        WHERE fecha = %s
        ORDER BY recibo DESC
    """
    results = await db.fetch_all(query, (fecha,))
    return results


@router.get("/resumen", response_model=ResumenDiaResponse)
async def get_resumen_por_rango_fecha(
    fecha_inicio: Annotated[date, Query(description="Fecha inicio YYYY-MM-DD")],
    fecha_fin: Annotated[date, Query(description="Fecha fin YYYY-MM-DD")],
    current_user: CurrentUserDep,
    db: Annotated[DatabaseConnection, Depends(get_db)],
):
    """Obtiene el resumen de ingresos por descripción en un rango de fechas."""
    query = """
        SELECT 
            descrip,
            COUNT(*) as total_recibos,
            SUM(total) as total
        FROM cxc
        WHERE fecha BETWEEN %s AND %s
        GROUP BY descrip
        ORDER BY total DESC
    """
    results = await db.fetch_all(query, (fecha_inicio, fecha_fin))
    return {"fecha_inicio": fecha_inicio, "fecha_fin": fecha_fin, "data": results}

from datetime import date
from typing import Annotated

from fastapi import APIRouter, Path, Query

from app.core.dependencies import CurrentUserDep
from app.db.connection import fetch_all
from app.schemas.ingreso import (
    IngresoAnualResponse,
    IngresoDiarioResponse,
    IngresoDiarioWrapper,
    ResumenDiaResponse,
)

router = APIRouter(prefix="/ingresos", tags=["ingresos"])


@router.get("/diarios", response_model=IngresoDiarioWrapper)
async def get_ingresos_diarios(
    fecha_inicio: Annotated[date, Query(description="Fecha inicio YYYY-MM-DD")],
    fecha_fin: Annotated[date, Query(description="Fecha fin YYYY-MM-DD")],
    current_user: CurrentUserDep,
):
    """Obtiene los ingresos en un rango de fechas."""
    query = """
        SELECT recibo, fecha, total, fpago, cliente, descrip, usuario
        FROM cxc
        WHERE fecha BETWEEN %s AND %s
        ORDER BY fecha DESC, recibo DESC
    """
    results = await fetch_all(query, (fecha_inicio, fecha_fin))
    total_general = sum(float(r["total"]) for r in results)
    return {"data": results, "total_general": total_general}


@router.get("/resumen", response_model=ResumenDiaResponse)
async def get_resumen_por_rango_fecha(
    fecha_inicio: Annotated[date, Query(description="Fecha inicio YYYY-MM-DD")],
    fecha_fin: Annotated[date, Query(description="Fecha fin YYYY-MM-DD")],
    current_user: CurrentUserDep,
):
    """Obtiene el resumen de ingresos por descripción en un rango de fechas."""
    query = """
        SELECT 
            fecha,
            descrip,
            COUNT(*) as total_recibos,
            SUM(total) as total
        FROM cxc
        WHERE fecha BETWEEN %s AND %s
        GROUP BY fecha, descrip
        ORDER BY fecha
    """
    results = await fetch_all(query, (fecha_inicio, fecha_fin))
    total_general = sum(float(r["total"]) for r in results)
    return {
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
        "data": results,
        "total_general": total_general,
    }


@router.get("/anual/{year}", response_model=IngresoAnualResponse)
async def get_ingresos_anuales(
    year: Annotated[int, Path(description="Año a consultar (ej: 2025)")],
    current_user: CurrentUserDep,
):
    """Obtiene los ingresos totales por mes para un año específico."""
    query = """
        SELECT 
            MONTH(fecha) as mes,
            COUNT(*) as total_recibos,
            SUM(total) as total
        FROM cxc
        WHERE YEAR(fecha) = %s
        GROUP BY MONTH(fecha)
        ORDER BY mes
    """
    results = await fetch_all(query, (year))

    results_dict = {r["mes"]: r for r in results}
    full_year = []
    for mes in range(1, 13):
        if mes in results_dict:
            full_year.append(results_dict[mes])
        else:
            full_year.append({"mes": mes, "total_recibos": 0, "total": 0.0})

    return {
        "year": year,
        "data": full_year,
        "total_general": sum(float(r["total"]) for r in full_year),
    }

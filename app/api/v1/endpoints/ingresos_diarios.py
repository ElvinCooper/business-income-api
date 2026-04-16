from datetime import date
from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, Query

from app.core.dependencies import CurrentUserDep
from app.db.connection import fetch_all
from app.schemas.ingreso import (
    IngresoAnualResponse,
    IngresoDiarioResponse,
    IngresoDiarioWrapper,
    ResumenDiaResponse,
    ResumenFormaPagoResponse,
    ResumenUsuarioResponse,
)

router = APIRouter(prefix="/ingresos", tags=["ingresos"])


@router.get(
    "/diarios",
    response_model=IngresoDiarioWrapper,
    summary="Ingresos diarios",
    description="Obtiene los ingresos (recibos) en un rango de fechas con su información detallada.",
    responses={
        200: {
            "description": "Lista de recibos en el rango de fechas",
            "content": {
                "application/json": {
                    "example": {
                        "data": [
                            {
                                "recibo": 1001,
                                "fecha": "2025-04-15",
                                "total": 1500.00,
                                "fpago": "Efectivo",
                                "cliente": "Juan Pérez",
                                "descrip": "Pago mensual",
                                "usuario": "admin",
                            },
                            {
                                "recibo": 1002,
                                "fecha": "2025-04-15",
                                "total": 2500.50,
                                "fpago": "Tarjeta",
                                "cliente": "María López",
                                "descrip": "Pago trimestral",
                                "usuario": "admin",
                            },
                        ],
                        "total_general": 4000.50,
                    }
                }
            },
        },
        401: {
            "description": "No autorizado",
            "content": {
                "application/json": {"example": {"detail": "Token inválido o expirado"}}
            },
        },
    },
)
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


@router.get(
    "/resumen",
    response_model=ResumenDiaResponse,
    summary="Resumen de ingresos",
    description="Obtiene el resumen de ingresos agrupados por descripción en un rango de fechas.",
    responses={
        200: {
            "description": "Resumen de ingresos por descripción",
            "content": {
                "application/json": {
                    "example": {
                        "fecha_inicio": "2025-04-01",
                        "fecha_fin": "2025-04-15",
                        "data": [
                            {
                                "fecha": "2025-04-15",
                                "descrip": "Pago mensual",
                                "total_recibos": 10,
                                "total": 15000.00,
                            },
                            {
                                "fecha": "2025-04-14",
                                "descrip": "Pago trimestral",
                                "total_recibos": 5,
                                "total": 12500.50,
                            },
                            {
                                "fecha": "2025-04-13",
                                "descrip": "Pago anual",
                                "total_recibos": 2,
                                "total": 24000.00,
                            },
                        ],
                        "total_general": 51500.50,
                    }
                }
            },
        },
        401: {
            "description": "No autorizado",
            "content": {
                "application/json": {"example": {"detail": "Token inválido o expirado"}}
            },
        },
        404: {
            "description": "No hay ingresos en el rango de fechas",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "No hay ingresos en el rango de fechas 2025-01-01 a 2025-01-31"
                    }
                }
            },
        },
    },
)
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
    if not results:
        raise HTTPException(
            status_code=404,
            detail=f"No hay ingresos en el rango de fechas {fecha_inicio} a {fecha_fin}",
        )
    total_general = sum(float(r["total"]) for r in results)
    return {
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
        "data": results,
        "total_general": total_general,
    }


@router.get(
    "/anual/{year}",
    response_model=IngresoAnualResponse,
    summary="Ingresos anuales",
    description="Obtiene los ingresos totales por mes para un año específico.",
    responses={
        200: {
            "description": "Ingresos anuales por mes",
            "content": {
                "application/json": {
                    "example": {
                        "year": 2025,
                        "data": [
                            {"mes": 1, "total_recibos": 45, "total": 67500.00},
                            {"mes": 2, "total_recibos": 38, "total": 57200.50},
                            {"mes": 3, "total_recibos": 52, "total": 78000.00},
                            {"mes": 4, "total_recibos": 40, "total": 60000.00},
                            {"mes": 5, "total_recibos": 0, "total": 0.0},
                            {"mes": 6, "total_recibos": 0, "total": 0.0},
                            {"mes": 7, "total_recibos": 0, "total": 0.0},
                            {"mes": 8, "total_recibos": 0, "total": 0.0},
                            {"mes": 9, "total_recibos": 0, "total": 0.0},
                            {"mes": 10, "total_recibos": 0, "total": 0.0},
                            {"mes": 11, "total_recibos": 0, "total": 0.0},
                            {"mes": 12, "total_recibos": 0, "total": 0.0},
                        ],
                        "total_general": 262700.50,
                    }
                }
            },
        },
        401: {
            "description": "No autorizado",
            "content": {
                "application/json": {"example": {"detail": "Token inválido o expirado"}}
            },
        },
    },
)
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


@router.get(
    "/usuarios",
    response_model=ResumenUsuarioResponse,
    summary="Ingresos por usuario",
    description="Obtiene el resumen de ingresos agrupados por usuario en un rango de fechas.",
    responses={
        200: {
            "description": "Resumen de ingresos por usuario",
            "content": {
                "application/json": {
                    "example": {
                        "fecha_inicio": "2025-04-01",
                        "fecha_fin": "2025-04-15",
                        "data": [
                            {
                                "usuario": "admin",
                                "forma_pago": "Efectivo",
                                "total_recibos": 25,
                                "total": 37500.00,
                            },
                            {
                                "usuario": "admin",
                                "forma_pago": "Tarjeta",
                                "total_recibos": 15,
                                "total": 22500.50,
                            },
                            {
                                "usuario": "cajero1",
                                "forma_pago": "Efectivo",
                                "total_recibos": 30,
                                "total": 45000.00,
                            },
                        ],
                        "total_general": 105000.50,
                    }
                }
            },
        },
        401: {
            "description": "No autorizado",
            "content": {
                "application/json": {"example": {"detail": "Token inválido o expirado"}}
            },
        },
    },
)
async def get_resumen_por_usuario(
    fecha_inicio: Annotated[date, Query(description="Fecha inicio YYYY-MM-DD")],
    fecha_fin: Annotated[date, Query(description="Fecha fin YYYY-MM-DD")],
    current_user: CurrentUserDep,
):
    """Obtiene el resumen de ingresos por usuario y forma de pago en un rango de fechas."""
    query = """
        SELECT 
            usuario,
            fpago as forma_pago,
            COUNT(*) as total_recibos,
            SUM(total) as total
        FROM cxc
        WHERE fecha BETWEEN %s AND %s
        GROUP BY usuario
        ORDER BY usuario, total DESC
    """
    results = await fetch_all(query, (fecha_inicio, fecha_fin))
    total_general = sum(float(r["total"]) for r in results)
    return {
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
        "data": results,
        "total_general": total_general,
    }


@router.get(
    "/formas-pago",
    response_model=ResumenFormaPagoResponse,
    summary="Ingresos por forma de pago",
    description="Obtiene el resumen de ingresos agrupados por forma de pago en un rango de fechas.",
    responses={
        200: {
            "description": "Resumen de ingresos por forma de pago",
            "content": {
                "application/json": {
                    "example": {
                        "fecha_inicio": "2025-04-01",
                        "fecha_fin": "2025-04-15",
                        "data": [
                            {
                                "fpago": "Efectivo",
                                "total_recibos": 55,
                                "total": 82500.00,
                            },
                            {
                                "fpago": "Tarjeta",
                                "total_recibos": 30,
                                "total": 45000.00,
                            },
                            {
                                "fpago": "Transferencia",
                                "total_recibos": 15,
                                "total": 22500.50,
                            },
                        ],
                        "total_general": 150000.50,
                    }
                }
            },
        },
        401: {
            "description": "No autorizado",
            "content": {
                "application/json": {"example": {"detail": "Token inválido o expirado"}}
            },
        },
    },
)
async def get_resumen_por_forma_pago(
    fecha_inicio: Annotated[date, Query(description="Fecha inicio YYYY-MM-DD")],
    fecha_fin: Annotated[date, Query(description="Fecha fin YYYY-MM-DD")],
    current_user: CurrentUserDep,
):
    """Obtiene el resumen de ingresos por forma de pago en un rango de fechas."""
    query = """
        SELECT 
            fpago,
            COUNT(*) as total_recibos,
            SUM(total) as total
        FROM cxc
        WHERE fecha BETWEEN %s AND %s
        GROUP BY fpago
        ORDER BY total DESC
    """
    results = await fetch_all(query, (fecha_inicio, fecha_fin))
    total_general = sum(float(r["total"]) for r in results)
    return {
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
        "data": results,
        "total_general": total_general,
    }

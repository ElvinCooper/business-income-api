from datetime import date, datetime, timedelta, timezone

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.core.dependencies import CurrentUserDep
from app.db.connection import fetch_one, fetch_all
from app.schemas.reporte import ReciboPago, ReporteVentasRequest
from app.utils.pdf_generator import (
    generar_recibo_termico,
    generar_reporte_ventas_termico,
)

router = APIRouter(prefix="/reportes", tags=["reportes"])


@router.post("/recibo")
async def crear_recibo(
    recibo: ReciboPago,
    current_user: CurrentUserDep,
):
    """Genera un recibo de pago en formato PDF térmico."""
    offset = timezone(timedelta(hours=-4))
    ahora = datetime.now(offset)
    ahora_str = ahora.strftime("%d-%m-%Y %H:%M")

    datos_recibo = {
        "nro_recibo": recibo.recibo,
        "cliente": recibo.cliente,
        "fecha": ahora_str,
        "monto": recibo.monto,
        "atendido_por": current_user.username,
        "empresa": current_user.empresa,
        "direccion": current_user.direccion,
        "telefono": current_user.telefono,
        "rnc": current_user.rnc,
        "proximo_pago": None,
        "usuario": None,
    }

    row_cxc = await fetch_one(
        "SELECT fechaprox, usuario FROM cxc WHERE recibo = %s",
        (recibo.recibo,),
    )
    if not row_cxc:
        raise HTTPException(status_code=404, detail="Recibo no encontrado")

    if row_cxc.get("fechaprox"):
        datos_recibo["proximo_pago"] = row_cxc["fechaprox"].strftime("%d-%m-%Y")
    if row_cxc.get("usuario"):
        datos_recibo["usuario"] = row_cxc["usuario"]

    try:
        comprobante = generar_recibo_termico(datos_recibo)
        fecha_filename = ahora.strftime("%Y%m%d")
        return StreamingResponse(
            comprobante,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=recibo_{datos_recibo['nro_recibo']}_{fecha_filename}.pdf"
            },
        )
    except Exception as err:
        raise HTTPException(
            status_code=500,
            detail=f"Error al generar recibo: {err}",
        )


@router.post("/ventas-termico")
async def crear_reporte_ventas_termico_endpoint(
    datos: ReporteVentasRequest,
    current_user: CurrentUserDep,
):
    """Genera un reporte de ventas en formato PDF térmico."""
    offset = timezone(timedelta(hours=-4))
    ahora = datetime.now(offset)
    ahora_str = ahora.strftime("%d-%m-%Y %H:%M")
    fecha_filename = ahora.strftime("%Y%m%d")

    condiciones = ["fecha BETWEEN %s AND %s"]
    params = (datos.desde, datos.hasta)

    where_clause = " AND ".join(condiciones)

    query = f"""
        SELECT 
            descrip,
            COUNT(*) as total_recibos,
            SUM(total) as total,
            fpago as tipo_pago
        FROM cxc
        WHERE {where_clause}
        GROUP BY descrip, fpago
        ORDER BY total DESC
    """
    rows = await fetch_all(query, params)

    if not rows:
        raise HTTPException(
            status_code=404,
            detail=f"No hay ventas en el rango de fechas {datos.desde} a {datos.hasta}",
        )

    items_dict: dict[str, float] = {}
    pagos_dict: dict[str, float] = {}
    total = 0.0

    for row in rows:
        descrip = row["descrip"]
        valor = float(row["total"]) if row["total"] else 0.0
        tipo = row["tipo_pago"]

        if descrip not in items_dict:
            items_dict[descrip] = 0.0
        items_dict[descrip] += valor

        if tipo:
            tipo_limpio = tipo.strip()
            if tipo_limpio not in pagos_dict:
                pagos_dict[tipo_limpio] = 0.0
            pagos_dict[tipo_limpio] += valor

        total += valor

    rows_fpago = await fetch_all(
        "SELECT DISTINCT TRIM(fpago) as fpago FROM cxc WHERE fpago IS NOT NULL AND fpago != ''"
    )
    todas_formas_pago = [row["fpago"] for row in rows_fpago]

    for forma in todas_formas_pago:
        if forma not in pagos_dict:
            pagos_dict[forma] = 0.0

    items = [{"descripcion": k, "valor": v} for k, v in items_dict.items()]
    pagos = [{"tipo": k, "valor": v} for k, v in pagos_dict.items()]

    datos_reporte = {
        "empresa": current_user.empresa,
        "direccion": current_user.direccion,
        "telefono": current_user.telefono,
        "rnc": current_user.rnc,
        "desde": datos.desde.strftime("%d-%m-%Y"),
        "hasta": datos.hasta.strftime("%d-%m-%Y"),
        "fecha_impresion": ahora_str,
        "usuario": current_user.username,
        "items": items,
        "total": total,
        "pagos": pagos,
    }

    pdf_buffer = generar_reporte_ventas_termico(datos_reporte)

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=reporte_ventas_{fecha_filename}.pdf"
        },
    )

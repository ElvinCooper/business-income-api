from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.core.dependencies import CurrentUserDep
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
        "nro_recibo": recibo.idnum,
        "cliente": recibo.cliente,
        "fecha": ahora_str,
        "monto": recibo.monto,
        "atendido_por": current_user.username,
    }

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
    pdf_buffer = generar_reporte_ventas_termico(datos.model_dump())

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=reporte_ventas.pdf"},
    )

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.core.dependencies import CurrentUserDep
from app.schemas.reporte import ReporteVentasRequest
from app.utils.pdf_generator import generar_reporte_ventas_termico

router = APIRouter(prefix="/reportes", tags=["reportes"])


@router.post("/ventas-termico")
async def crear_reporte_ventas_termico(
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

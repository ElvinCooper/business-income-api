from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    ingresos_diarios,
    ingresos_rango,
    ingresos_grafica,
)

router = APIRouter(prefix="/v1")

router.include_router(auth.router)
router.include_router(ingresos_diarios.router)
router.include_router(ingresos_rango.router)
router.include_router(ingresos_grafica.router)

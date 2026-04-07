from fastapi import APIRouter

from app.api.v1.endpoints import auth, ingresos_diarios, reportes, test_errors

router = APIRouter(prefix="/v1")

router.include_router(auth.router)
router.include_router(ingresos_diarios.router)
router.include_router(reportes.router)
router.include_router(test_errors.router)

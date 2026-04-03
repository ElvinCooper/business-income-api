from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer

from app.core.dependencies import CurrentUserDep
from app.core.security import create_access_token
from app.db.connection import DatabaseConnection, get_db
from app.schemas.auth import LoginRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])

security = HTTPBearer(auto_error=False)


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: LoginRequest,
    db: Annotated[DatabaseConnection, Depends(get_db)],
):
    """Autentica al usuario y devuelve un token JWT."""
    pass

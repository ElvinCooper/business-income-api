from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.security import create_access_token
from app.db.connection import DatabaseConnection, get_db
from app.schemas.auth import LoginRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: LoginRequest,
    db: Annotated[DatabaseConnection, Depends(get_db)],
):
    """Autentica al usuario y devuelve un token JWT."""
    query = """
        SELECT idusuario, usuario, clave, fullname
        FROM usuario
        WHERE usuario = %s
    """
    user = await db.fetch_one(query, (credentials.username,))

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
        )

    if credentials.password != user["clave"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
        )

    access_token = create_access_token(
        data={"sub": str(user["idusuario"]), "username": user["usuario"]}
    )

    return TokenResponse(access_token=access_token)

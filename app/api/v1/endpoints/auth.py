from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.security import create_access_token
from app.db.connection import fetch_one
from app.schemas.auth import CurrentUserResponse, LoginRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
async def login(credentials: LoginRequest):
    """Autentica al usuario y devuelve un token JWT."""
    query = """
        SELECT idusuario, usuario, clave, fullname
        FROM usuario
        WHERE usuario = %s
    """
    user = await fetch_one(query, (credentials.username,))

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
        data={
            "sub": str(user["idusuario"]),
            "username": user["usuario"],
            "fullname": user["fullname"],
        }
    )

    return TokenResponse(access_token=access_token)


@router.get("/me", response_model=CurrentUserResponse)
async def get_current_user(
    current_user: Annotated[dict, Depends("app.core.dependencies.get_current_user")],
):
    """Obtiene la información del usuario actualmente logueado."""
    return CurrentUserResponse(
        idusuario=current_user["user_id"],
        usuario=current_user["username"],
        fullname=current_user["fullname"],
    )


@router.post("/logout")
async def logout(
    current_user: Annotated[dict, Depends("app.core.dependencies.get_current_user")],
):
    """Cierra la sesión del usuario."""
    return {"message": "Sesión cerrada exitosamente"}

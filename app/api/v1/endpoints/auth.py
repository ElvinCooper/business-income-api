from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.dependencies import CurrentUserDep
from app.core.security import create_access_token, decode_access_token
from app.db.connection import fetch_one
from app.db.postgres import add_token_to_blocklist
from app.schemas.auth import CurrentUserResponse, LoginRequest, TokenResponse

security = HTTPBearer(auto_error=False)


router = APIRouter(prefix="/auth", tags=["auth"])


def _add_token_blocklist(jti: str, idusuario: int):
    """Agrega el token a la blocklist en PostgreSQL"""
    add_token_to_blocklist(jti, idusuario)


@router.post("/login", response_model=TokenResponse)
async def login(credentials: LoginRequest):
    """Autentica al usuario y devuelve un token JWT."""
    query = """
        SELECT us.idusuario, us.usuario, us.clave, us.fullname, us.cia, 
               su.empresa, su.direccion, su.telefono
        FROM usuario us 
        JOIN sucursal su ON us.cia = su.idcia
        WHERE us.usuario = %s
    """
    user = await fetch_one(query, (credentials.usuario,))

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
        )

    if credentials.clave != user["clave"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
        )

    access_token = create_access_token(
        data={
            "sub": str(user["idusuario"]),
            "username": user["usuario"],
            "fullname": user["fullname"],
            "cia": int(user["cia"]),
            "empresa": user["empresa"],
            "direccion": user.get("direccion", ""),
            "telefono": user.get("telefono", ""),
            "rnc": user.get("rnc") if "rnc" in user else "",
        }
    )

    return TokenResponse(
        access_token=access_token,
        idusuario=user["idusuario"],
        usuario=user["usuario"],
        fullname=user["fullname"],
        cia=int(user["cia"]),
        empresa=user["empresa"],
    )


@router.get("/me", response_model=CurrentUserResponse)
async def get_current_user_info(current_user: CurrentUserDep):
    """Obtiene la información del usuario desde el token JWT."""
    return CurrentUserResponse(
        idusuario=current_user.user_id,
        usuario=current_user.username,
        fullname=current_user.fullname,
        cia=current_user.cia,
        empresa=current_user.empresa,
    )


@router.post("/logout")
async def logout(
    background_tasks: BackgroundTasks,
    current_user: CurrentUserDep,
):
    """Cierra la sesión del usuario agregando el token a la blocklist."""
    if current_user.jti:
        background_tasks.add_task(
            _add_token_blocklist, current_user.jti, current_user.user_id
        )
    return {"message": "Sesión cerrada exitosamente"}

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.security import create_access_token, decode_access_token
from app.db.connection import fetch_one
from app.schemas.auth import CurrentUserResponse, LoginRequest, TokenResponse

security = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
) -> dict:
    """Dependencia para obtener el usuario desde el token JWT"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token no proporcionado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    payload = decode_access_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {
        "idusuario": payload.get("sub"),
        "username": payload.get("username"),
        "fullname": payload.get("fullname"),
        "cia": payload.get("cia"),
        "empresa": payload.get("empresa"),
    }


CurrentUserDep = Annotated[dict, Depends(get_current_user)]

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
async def login(credentials: LoginRequest):
    """Autentica al usuario y devuelve un token JWT."""
    query = """
        SELECT us.idusuario, us.usuario, us.clave, us.fullname, us.cia, su.empresa
        FROM usuario us 
        JOIN sucursal su ON us.cia = su.idcia
        WHERE us.usuario = %s
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
            "cia": int(user["cia"]),
            "empresa": user["empresa"],
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
        idusuario=int(current_user["idusuario"]),
        usuario=current_user["username"],
        fullname=current_user["fullname"],
        cia=int(current_user["cia"]),
        empresa=current_user["empresa"],
    )


@router.post("/logout")
async def logout():
    """Cierra la sesión del usuario."""
    return {"message": "Sesión cerrada exitosamente"}

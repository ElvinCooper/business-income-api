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


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Iniciar sesión",
    description="Autentica al usuario con las credenciales proporcionadas. "
    "El parámetro **bd** es el nombre de la base de datos del cliente. "
    "Si la BD, el usuario o la clave son incorrectos, devuelve error 401.",
    responses={
        401: {
            "description": "Credenciales incorrectas (BD, usuario o contraseña inválidos)",
            "content": {
                "application/json": {"example": {"detail": "Credenciales incorrectas"}}
            },
        }
    },
)
async def login(credentials: LoginRequest):
    """Iniciar sesión en el sistema.

    Autentica usando:
    - **usuario**: nombre de usuario
    - **clave**: contraseña
    - **bd**: nombre de la base de datos del cliente

    Si la BD no existe, el usuario no existe o la clave es incorrecta,
    devuelve 401 con el mensaje "Credenciales incorrectas".
    """
    query = """
        SELECT us.idusuario, us.usuario, us.clave, us.fullname, us.cia, 
               su.empresa, su.direccion, su.telefono
        FROM usuario us 
        JOIN sucursal su ON us.cia = su.idcia
        WHERE us.usuario = %s
    """
    try:
        db_name = credentials.bd.strip().lower()
        usuario = credentials.usuario.strip()
        clave = credentials.clave.strip()
        user = await fetch_one(query, (usuario,), db_name=db_name)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
        )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
        )

    if clave != user["clave"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
        )

    access_token = create_access_token(
        data={
            "sub": str(user["idusuario"]),
            "username": user["usuario"],
            "fullname": user["fullname"],
            "cia": int(user["cia"]),
            "empresa": user["empresa"],
            "db_name": credentials.bd,
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
        db_name=credentials.bd,
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
        db_name=current_user.db_name,
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

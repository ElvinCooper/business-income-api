from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from app.core.security import decode_access_token
from app.db.postgres import is_token_revoked


security = HTTPBearer(auto_error=False)


class CurrentUser(BaseModel):
    user_id: int
    username: str
    fullname: str
    cia: int
    empresa: str
    direccion: str = ""
    telefono: str = ""
    rnc: str = ""
    jti: str


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
) -> CurrentUser:
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

    jti = payload.get("jti")
    if jti and is_token_revoked(jti):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token ha sido revocado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    username = payload.get("username")
    fullname = payload.get("fullname", username)
    cia = payload.get("cia")
    empresa = payload.get("empresa")
    direccion = payload.get("direccion", "")
    telefono = payload.get("telefono", "")
    rnc = payload.get("rnc", "")

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return CurrentUser(
        user_id=int(user_id),
        username=str(username),
        fullname=str(fullname),
        cia=int(cia) if cia else 0,
        empresa=str(empresa) if empresa else "",
        direccion=str(direccion),
        telefono=str(telefono),
        rnc=str(rnc),
        jti=str(jti) if jti else "",
    )


CurrentUserDep = Annotated[CurrentUser, Depends(get_current_user)]

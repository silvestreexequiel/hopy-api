from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from ..config import settings
from ..security import issue_token

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


class LoginBody(BaseModel):
    username: str = ""
    password: str = ""


@router.post("/login")
def login(body: LoginBody):
    username = body.username
    password = body.password

    if settings.staff_user is None or settings.staff_pass is None:
        return JSONResponse(
            status_code=500,
            content={"ok": False, "error": "Configuracion incompleta: faltan credenciales staff."},
        )

    if username == settings.staff_user and password == settings.staff_pass:
        token = issue_token(username, role="staff")
        return {
            "ok": True,
            "token": token,
            "user": {"username": username, "role": "staff"},
        }

    return JSONResponse(
        status_code=401,
        content={"ok": False, "error": f"Credenciales invalidas para {username}"},
    )

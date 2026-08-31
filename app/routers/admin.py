from fastapi import APIRouter, Header
from fastapi.responses import JSONResponse

from .. import db
from ..config import settings
from ..security import identity_from_header
from .profiles import PROFILES

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


@router.get("/overview")
def overview(authorization: str = Header(default=None)):
    identity = identity_from_header(authorization)
    if identity is None:
        return JSONResponse(status_code=401, content={"ok": False, "error": "Authentication required."})

    if identity.get("role") != "admin":
        return JSONResponse(
            status_code=403,
            content={"ok": False, "error": "Admin role required.", "your_role": identity.get("role")},
        )

    return {
        "ok": True,
        "viewer": identity.get("sub"),
        "total_events": db.count_cleanup_events(),
        "staff_directory": [
            {"id": pid, **data} for pid, data in PROFILES.items()
        ],
        "config": {
            "db_host": settings.db_host,
            "db_name": settings.db_name,
            "openai_model": settings.openai_model,
            "staff_user": settings.staff_user,
        },
    }

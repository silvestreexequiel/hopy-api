import json
import random

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from .. import db
from ..config import settings
from ..security import parse_basic_auth

router = APIRouter(prefix="/api/v1/cleanup", tags=["cleanup"])

JOBS = {
    "orphans": {
        "endpoint": "/api/v1/cleanup/orphans",
        "category": "users",
        "message": "Orphan user accounts erased. Records permanently removed from the database.",
    },
    "logs": {
        "endpoint": "/api/v1/cleanup/logs",
        "category": "logs",
        "message": "Legacy logs deleted. Log files removed from disk permanently.",
    },
    "cache": {
        "endpoint": "/api/v1/cleanup/cache",
        "category": "cache",
        "message": "Stale cache purged. Cache store flushed and invalidated.",
    },
}


async def _run_job(job_key, request: Request):
    job = JOBS[job_key]
    raw = (await request.body()).decode("utf-8", "ignore")
    try:
        payload = json.loads(raw) if raw else {}
        if not isinstance(payload, dict):
            payload = {"raw": raw}
    except json.JSONDecodeError:
        payload = {"raw": raw}

    db_status = "not_logged"
    try:
        db.register_cleanup_trigger(
            job["category"],
            job["endpoint"],
            "DELETE",
            raw,
            request.client.host if request.client else None,
            request.headers.get("user-agent"),
        )
        db_status = "logged"
    except Exception:
        db_status = "db_error"

    return {
        "ok": True,
        "endpoint": job["endpoint"],
        "received_method": "DELETE",
        "job_id": "JOB-" + str(random.randint(10000, 99999)),
        "message": job["message"],
        "received_payload": payload,
        "db_tracking": db_status,
    }


@router.delete("/orphans")
async def cleanup_orphans(request: Request):
    return await _run_job("orphans", request)


@router.delete("/logs")
async def cleanup_logs(request: Request):
    return await _run_job("logs", request)


@router.delete("/cache")
async def cleanup_cache(request: Request):
    return await _run_job("cache", request)


def _deny(status, message, challenge=False):
    headers = {}
    if challenge:
        headers["WWW-Authenticate"] = 'Basic realm="Academy Operations Admin", charset="UTF-8"'
    return JSONResponse(status_code=status, content={"ok": False, "error": message}, headers=headers)


@router.api_route("/reset", methods=["GET", "POST", "DELETE"])
def cleanup_reset(request: Request):
    if settings.admin_user is None or settings.admin_pass is None:
        return JSONResponse(
            status_code=500,
            content={"ok": False, "error": "Server misconfigured: admin credentials are not set."},
        )

    creds = parse_basic_auth(request.headers.get("authorization"))
    if creds is None:
        return _deny(401, "Authentication required.", challenge=True)

    user, pwd = creds
    import hmac

    user_ok = hmac.compare_digest(str(settings.admin_user), str(user))
    pass_ok = hmac.compare_digest(str(settings.admin_pass), str(pwd))
    if not (user_ok and pass_ok):
        return _deny(401, "Invalid credentials.", challenge=True)

    try:
        result = db.purge_cleanup_events()
    except Exception as exc:
        return JSONResponse(
            status_code=500,
            content={"ok": False, "error": "Reset failed: " + str(exc)},
        )

    return {
        "ok": True,
        "endpoint": "/api/v1/cleanup/reset",
        "received_method": request.method,
        "message": "Cleanup event log erased.",
        "deleted_events": result["deleted_events"],
        "legacy_counters_reset": result["legacy_counters_reset"],
    }

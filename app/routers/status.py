from fastapi import APIRouter

router = APIRouter(prefix="/api/v1", tags=["status"])


@router.get("/status")
def status(status: str = "System healthy"):
    return {"ok": True, "status": status, "refresh_seconds": 300}

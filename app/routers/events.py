from fastapi import APIRouter, Query

from .. import db

router = APIRouter(prefix="/api/v1", tags=["events"])


@router.get("/events")
def search_events(q: str = Query(default="")):
    """Buscador de eventos de limpieza por categoria, endpoint o IP."""
    results = []
    error = None

    if q != "":
        condition = (
            "category LIKE '%" + q + "%' "
            "OR endpoint LIKE '%" + q + "%' "
            "OR remote_addr LIKE '%" + q + "%'"
        )
        try:
            results = db.raw_search_events(condition)
        except Exception as exc:
            error = str(exc)

    payload = {
        "ok": error is None,
        "query": q,
        "message": f"Resultados para: {q}" if q != "" else "Sin filtro aplicado.",
        "count": len(results),
        "results": results,
    }
    if error is not None:
        payload["error"] = error
    return payload


@router.get("/cleanup/events")
def cleanup_events(page: int = 1, per_page: int = 25):
    if per_page not in (25, 50, 100, 200):
        per_page = 25
    if page < 1:
        page = 1

    total = db.count_cleanup_events()
    total_pages = (total + per_page - 1) // per_page if total > 0 else 1
    if page > total_pages:
        page = total_pages

    rows = db.get_cleanup_events(per_page, (page - 1) * per_page)
    for row in rows:
        if row.get("triggered_at") is not None:
            row["triggered_at"] = str(row["triggered_at"])

    return {
        "ok": True,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages,
        "events": rows,
    }

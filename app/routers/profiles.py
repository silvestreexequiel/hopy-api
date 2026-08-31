from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/profiles", tags=["profiles"])

PROFILES = {
    "1001": {"name": "Lucia Perez", "role": "Operations Lead", "email": "lucia@academy.local"},
    "1002": {"name": "Martin Silva", "role": "Data Analyst", "email": "martin@academy.local"},
    "1003": {"name": "Paula Rios", "role": "Compliance", "email": "paula@academy.local"},
}


@router.get("/{profile_id}")
def get_profile(profile_id: str):
    profile = PROFILES.get(
        profile_id, {"name": "Unknown", "role": "N/A", "email": "N/A"}
    )
    return {"id": profile_id, **profile}

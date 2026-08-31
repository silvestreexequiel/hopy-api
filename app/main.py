from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import auth, profiles, events, cleanup, chat, status, admin

app = FastAPI(title="Academy Operations API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(profiles.router)
app.include_router(events.router)
app.include_router(cleanup.router)
app.include_router(chat.router)
app.include_router(status.router)
app.include_router(admin.router)


@app.api_route("/", methods=["GET", "HEAD"])
def root():
    return {
        "service": "Academy Operations API",
        "version": "1.0.0",
        "endpoints": [
            "POST /api/v1/auth/login",
            "GET /api/v1/profiles/{id}",
            "GET /api/v1/events?q=",
            "GET /api/v1/cleanup/events",
            "DELETE /api/v1/cleanup/orphans|logs|cache",
            "DELETE /api/v1/cleanup/reset",
            "POST /api/v1/chat",
            "GET /api/v1/status",
            "GET /api/v1/admin/overview",
        ],
    }

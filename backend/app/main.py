from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.drone import router as drone_router
from app.routes.health import router as health_router
from app.routes.missions import router as missions_router


def create_app() -> FastAPI:
    application = FastAPI(
        title="Vimantra AI Mission Planner API",
        version="1.0.0-rc1",
    )
    application.add_middleware(
        CORSMiddleware,
        allow_credentials=False,
        allow_headers=["*"],
        allow_methods=["*"],
        allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    )
    application.include_router(drone_router)
    application.include_router(health_router)
    application.include_router(missions_router)
    return application


app = create_app()

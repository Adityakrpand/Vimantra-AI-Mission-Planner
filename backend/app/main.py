from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.drone import router as drone_router
from app.routes.health import router as health_router
from app.routes.missions import api_router as mission_validation_router
from app.routes.missions import router as missions_router
from config.settings import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    application = FastAPI(
        title="Vimantra AI Mission Planner API",
        version="1.0.0-rc1",
        debug=settings.debug,
    )
    application.add_middleware(
        CORSMiddleware,
        allow_credentials=False,
        allow_headers=["*"],
        allow_methods=["*"],
        allow_origins=settings.cors_origins,
    )
    application.include_router(drone_router)
    application.include_router(health_router)
    application.include_router(mission_validation_router)
    application.include_router(missions_router)
    return application


app = create_app()

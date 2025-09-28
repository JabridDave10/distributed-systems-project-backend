from fastapi import FastAPI
from app.core.middleware import configure_middleware
from app.core.database import create_tables
from app.modules.citas.routers import health, citas
from app.modules.auth.routers.user_router import router as user_router
from app.modules.auth.routers.auth_router import router as auth_router
from app.modules.register.routers.register_router import router as register_router

app = FastAPI(title="Distributed Systems Project - Backend", version="0.1.0")

# Configurar middleware (CORS u otros)
configure_middleware(app)

@app.on_event("startup")
async def startup_event():
    create_tables()

app.include_router(health.router)
app.include_router(citas.router)  # Main appointments router
app.include_router(citas.legacy_router)  # Legacy compatibility router
app.include_router(user_router)
app.include_router(auth_router)
app.include_router(register_router)

@app.get("/")
def read_root():
    return {
        "message": "Backend funcionando 🚀",
        "endpoints": {
            "health": "/health/",
            "appointments": "/appointments/",
            "citas": "/citas/",  # Legacy endpoint
            "users": "/users/",
            "auth": "/auth/",
            "register": "/register/",
            "test_connection": "/citas/test/connection"
        }
    }

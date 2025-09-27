from fastapi import FastAPI
from app.core.middleware import configure_middleware
from app.core.database import create_tables
from app.modules.citas.routers import health, citas

app = FastAPI(title="Distributed Systems Project - Backend", version="0.1.0")

# Configurar middleware (CORS u otros)
configure_middleware(app)

@app.on_event("startup")
async def startup_event():
    create_tables()

app.include_router(health.router)
app.include_router(citas.router)

@app.get("/")
def read_root():
    return {
        "message": "Backend funcionando 🚀",
        "endpoints": {
            "health": "/health/",
            "citas": "/citas/",
            "test_connection": "/citas/test/connection"
        }
    }

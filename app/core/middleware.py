from fastapi.middleware.cors import CORSMiddleware
import os

def configure_middleware(app):
    origins = [
        "http://localhost:3000",
        "http://localhost:5173", # Vite dev server
        "http://localhost:5174", # Vite dev server alternativo
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]

    # En producción, añadir el dominio del frontend si está configurado
    frontend_url = os.environ.get("FRONTEND_URL")
    if frontend_url:
        origins.append(frontend_url)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

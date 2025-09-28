from fastapi.middleware.cors import CORSMiddleware

def configure_middleware(app):
    origins = [
        "http://localhost:3000",
        "http://localhost:5173", # frontend local
        "http://localhost:5174"  # frontend Desarrollo
        # Agrega aquí dominios de producción cuando subas el proyecto
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

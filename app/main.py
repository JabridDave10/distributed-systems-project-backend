from fastapi import FastAPI
from app.middleware import configure_middleware

app = FastAPI(title="Distributed Systems Project - Backend", version="0.1.0")

# Configurar middleware (CORS u otros)
configure_middleware(app)

@app.get("/")
def read_root():
    return {"message": "Backend funcionando 🚀"}

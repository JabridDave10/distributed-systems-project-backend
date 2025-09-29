#!/usr/bin/env python3
import os
import uvicorn

def main():
    # Obtener el puerto desde la variable de entorno (Render usa 10000 por defecto)
    port = int(os.environ.get("PORT", 10000))

    print(f"🚀 Iniciando servidor en puerto: {port}")
    print(f"📡 Host: 0.0.0.0")
    print(f"🔧 Entorno PORT: {os.environ.get('PORT', 'No configurado')}")
    print(f"🌐 Variables de entorno disponibles: {list(os.environ.keys())}")

    # Iniciar uvicorn SIN reload para producción
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        workers=1,
        reload=False,  # CRÍTICO: Sin reload en producción
        access_log=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()
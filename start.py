#!/usr/bin/env python3
import os
import uvicorn

def main():
    # Obtener el puerto desde la variable de entorno
    port = int(os.environ.get("PORT", 8000))

    print(f"🚀 Iniciando servidor en puerto: {port}")
    print(f"📡 Host: 0.0.0.0")
    print(f"🔧 Entorno PORT: {os.environ.get('PORT', 'No configurado')}")

    # Iniciar uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        workers=1,
        access_log=True
    )

if __name__ == "__main__":
    main()
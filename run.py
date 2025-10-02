"""
Punto de entrada para lanzar la aplicación FastAPI.
"""

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "src.infrastructure.fastapi.app:app",
        host="0.0.0.0",
        port=5005,
        reload=True
    )

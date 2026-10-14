from fastapi import FastAPI

from pixelguard.api.routes import router

app = FastAPI(
    title="PixelGuard",
    description="Auditor técnico de imágenes de producto.",
    version="0.1.0",
)

app.include_router(router)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}

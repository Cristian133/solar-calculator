from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import sol

app = FastAPI(title="Calculadora Solar API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(sol.router, prefix="/sol", tags=["sol"])

# El resto de los routers por feature (docs/plan_tecnico.md, sección 5) se
# agregan acá a medida que se implementan.

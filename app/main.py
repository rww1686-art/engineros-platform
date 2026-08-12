from fastapi import FastAPI

from app.api.companies import router as companies_router
from app.api.company_competencies import router as company_competencies_router
from app.api.competencies import router as competencies_router
from app.api.regions import router as regions_router
from app.api.verify import router as verify_router
from app.core.config import get_settings

settings = get_settings()
app = FastAPI(title=settings.app_name, version="0.2.0")
app.include_router(companies_router)
app.include_router(company_competencies_router)
app.include_router(regions_router)
app.include_router(competencies_router)
app.include_router(verify_router)


@app.get("/health", tags=["system"])
def health_check() -> dict[str, str]:
    return {"status": "ok", "environment": settings.app_environment}

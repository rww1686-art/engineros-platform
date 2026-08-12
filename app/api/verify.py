from fastapi import APIRouter

from app.schemas.verify import (
    HVACVerificationInput,
    HVACVerificationResult,
    ProjectVerificationInput,
    ProjectVerificationResult,
)
from app.services.verify import verify_hvac
from app.services.verify_kernel import verify_project

router = APIRouter(prefix="/verify", tags=["verify"])


@router.post("/hvac", response_model=HVACVerificationResult)
def run_hvac_verification(payload: HVACVerificationInput) -> HVACVerificationResult:
    """Run deterministic P0 HVAC project verification."""
    return verify_hvac(payload)


@router.post("/project", response_model=ProjectVerificationResult)
def run_project_verification(payload: ProjectVerificationInput) -> ProjectVerificationResult:
    """Run evidence-driven project verification with critic and release gates."""
    return verify_project(payload)

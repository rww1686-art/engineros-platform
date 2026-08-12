from fastapi import APIRouter

from app.schemas.verify import HVACVerificationInput, HVACVerificationResult
from app.services.verify import verify_hvac

router = APIRouter(prefix="/verify", tags=["verify"])


@router.post("/hvac", response_model=HVACVerificationResult)
def run_hvac_verification(payload: HVACVerificationInput) -> HVACVerificationResult:
    """Run deterministic P0 HVAC project verification."""
    return verify_hvac(payload)

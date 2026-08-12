from dataclasses import dataclass

from app.schemas.verify import HVACVerificationResult, VerificationStatus
from app.services.evidence_gate import DesignPointEvidenceResult


@dataclass(frozen=True)
class CustomerGradeReadinessResult:
    status: VerificationStatus
    customer_grade: bool
    reason: str
    source_id: str | None


def evaluate_customer_grade_readiness(
    *,
    verification: HVACVerificationResult,
    equipment_evidence: DesignPointEvidenceResult,
) -> CustomerGradeReadinessResult:
    """Prevent a customer-grade PASS without exact design-point manufacturer evidence."""
    if verification.status == VerificationStatus.FAIL:
        return CustomerGradeReadinessResult(
            status=VerificationStatus.FAIL,
            customer_grade=False,
            reason="Engineering verification contains a FAIL finding.",
            source_id=equipment_evidence.source_id,
        )

    if not equipment_evidence.covered:
        return CustomerGradeReadinessResult(
            status=VerificationStatus.INSUFFICIENT_DATA,
            customer_grade=False,
            reason=(
                "Exact manufacturer equipment-capacity evidence is unavailable "
                "for the project design condition."
            ),
            source_id=None,
        )

    if verification.status in {
        VerificationStatus.REVIEW_REQUIRED,
        VerificationStatus.INSUFFICIENT_DATA,
        VerificationStatus.NOT_ASSESSED,
    }:
        return CustomerGradeReadinessResult(
            status=verification.status,
            customer_grade=False,
            reason="The engineering verification is not in an acceptable final state.",
            source_id=equipment_evidence.source_id,
        )

    return CustomerGradeReadinessResult(
        status=verification.status,
        customer_grade=True,
        reason="Engineering checks and exact design-point equipment evidence are available.",
        source_id=equipment_evidence.source_id,
    )

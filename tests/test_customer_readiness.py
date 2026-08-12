from app.schemas.verify import HVACVerificationResult, VerificationStatus
from app.services.customer_readiness import evaluate_customer_grade_readiness
from app.services.evidence_gate import DesignPointEvidenceResult


def _verification(status: VerificationStatus) -> HVACVerificationResult:
    return HVACVerificationResult(
        object_id="GOLD-B-001",
        status=status,
        findings=[],
        assessed_checks=4,
        failed_checks=0,
    )


def test_customer_grade_pass_blocked_without_exact_manufacturer_evidence() -> None:
    result = evaluate_customer_grade_readiness(
        verification=_verification(VerificationStatus.PASS),
        equipment_evidence=DesignPointEvidenceResult(
            covered=False,
            source_id=None,
            capacity_kw=None,
            reason="No exact manufacturer evidence point is available.",
        ),
    )

    assert result.customer_grade is False
    assert result.status == VerificationStatus.INSUFFICIENT_DATA


def test_customer_grade_pass_allowed_with_exact_manufacturer_evidence() -> None:
    result = evaluate_customer_grade_readiness(
        verification=_verification(VerificationStatus.PASS),
        equipment_evidence=DesignPointEvidenceResult(
            covered=True,
            source_id="EEO-MANUFACTURER-DESIGN-POINT",
            capacity_kw=15.2,
            reason="Exact manufacturer evidence point is available.",
        ),
    )

    assert result.customer_grade is True
    assert result.status == VerificationStatus.PASS
    assert result.source_id == "EEO-MANUFACTURER-DESIGN-POINT"

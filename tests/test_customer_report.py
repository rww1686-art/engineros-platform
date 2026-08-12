from app.schemas.verify import HVACVerificationInput, EOR, VerificationStatus
from app.services.customer_readiness import evaluate_customer_grade_readiness
from app.services.evidence_gate import DesignPointEvidenceResult
from app.services.verify import verify_hvac
from app.services.verify_report import render_customer_verification_report


def test_customer_report_never_presents_core_pass_as_final_without_evidence() -> None:
    verification = verify_hvac(
        HVACVerificationInput(
            object=EOR(object_id="GOLD-B-001", name="GOLD baseline"),
            declared_heat_load_kw=15.2,
            independent_heat_load_kw=15.174,
            equipment_capacity_kw=16.0,
            design_flow_m3_h=2.61,
            required_flow_m3_h=2.609,
            drawing_equipment_capacity_kw=16.0,
            calculation_equipment_capacity_kw=16.0,
            specification_equipment_capacity_kw=16.0,
        )
    )
    assert verification.status == VerificationStatus.PASS

    readiness = evaluate_customer_grade_readiness(
        verification=verification,
        equipment_evidence=DesignPointEvidenceResult(
            covered=False,
            source_id=None,
            capacity_kw=None,
            reason="No exact manufacturer evidence point.",
        ),
    )
    report = render_customer_verification_report(verification, readiness)

    assert "Final customer status: **INSUFFICIENT DATA**" in report
    assert "Core verification status: **PASS**" in report
    assert "Customer-grade: **NO**" in report
    assert "Final customer status: **PASS**" not in report


def test_customer_report_allows_final_pass_with_exact_evidence() -> None:
    verification = verify_hvac(
        HVACVerificationInput(
            object=EOR(object_id="REAL-B-001", name="Verified project"),
            declared_heat_load_kw=14.8,
            independent_heat_load_kw=14.8,
            equipment_capacity_kw=15.0,
            design_flow_m3_h=2.55,
            required_flow_m3_h=2.54,
            drawing_equipment_capacity_kw=15.0,
            calculation_equipment_capacity_kw=15.0,
            specification_equipment_capacity_kw=15.0,
        )
    )
    readiness = evaluate_customer_grade_readiness(
        verification=verification,
        equipment_evidence=DesignPointEvidenceResult(
            covered=True,
            source_id="EEO-MANUFACTURER-DESIGN-POINT",
            capacity_kw=15.0,
            reason="Exact manufacturer evidence point is available.",
        ),
    )
    report = render_customer_verification_report(verification, readiness)

    assert readiness.customer_grade is True
    assert "Final customer status: **PASS**" in report
    assert "Customer-grade: **YES**" in report
    assert "EEO-MANUFACTURER-DESIGN-POINT" in report

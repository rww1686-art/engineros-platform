from fastapi.testclient import TestClient

from app.main import app
from app.schemas.verify import (
    EEO,
    GateType,
    ProjectCheckInput,
    ProjectVerificationInput,
    VerificationStatus,
)
from app.services.verify_kernel import verify_project

client = TestClient(app)


def _evidence(evidence_id: str) -> EEO:
    return EEO(
        evidence_id=evidence_id,
        object_id="GP-001",
        source_type="drawing",
        source="164-04-2026.pdf",
        locator="sheet/test locator",
    )


def test_kernel_does_not_stop_after_first_fail() -> None:
    payload = ProjectVerificationInput(
        project_id="GP-001",
        evidence_objects=[_evidence("E-01"), _evidence("E-02")],
        expected_check_ids=["GP001-ETR-01", "GP001-REV-01"],
        checks=[
            ProjectCheckInput(
                check_id="GP001-ETR-01",
                title="19.1 A versus C16",
                discipline="ETR",
                severity="CRITICAL",
                proposed_status=VerificationStatus.FAIL,
                message="Розрахунковий струм 19,1 А перевищує номінал C16.",
                evidence_ids=["E-01"],
                gates=[GateType.PROCUREMENT, GateType.INSTALLATION, GateType.RELEASE],
            ),
            ProjectCheckInput(
                check_id="GP001-REV-01",
                title="Revision conflict",
                discipline="AB/TX/VK",
                severity="HIGH",
                proposed_status=VerificationStatus.FAIL,
                message="Розділи використовують різні редакції вихідної основи.",
                evidence_ids=["E-02"],
                gates=[GateType.DESIGN, GateType.RELEASE],
            ),
        ],
    )

    result = verify_project(payload)

    assert result.status == VerificationStatus.FAIL
    assert result.completed_checks == 2
    assert result.coverage_pct == 100.0
    assert result.failed_checks == 2
    assert {f.finding_id for f in result.findings if f.status == VerificationStatus.FAIL} == {
        "GP001-ETR-01",
        "GP001-REV-01",
    }
    assert result.release_allowed is False


def test_critic_downgrades_unsupported_critical_fail_to_hold() -> None:
    result = verify_project(
        ProjectVerificationInput(
            project_id="GP-001",
            expected_check_ids=["GP001-UNSUPPORTED"],
            checks=[
                ProjectCheckInput(
                    check_id="GP001-UNSUPPORTED",
                    title="Unsupported critical claim",
                    discipline="HVAC",
                    severity="CRITICAL",
                    proposed_status=VerificationStatus.FAIL,
                    message="Критичне твердження без зареєстрованого доказу.",
                    evidence_ids=["MISSING-EVIDENCE"],
                    gates=[GateType.RELEASE],
                )
            ],
        )
    )

    assert result.status == VerificationStatus.HOLD
    assert result.findings[0].status == VerificationStatus.HOLD
    assert result.failed_checks == 0
    assert result.hold_checks == 1
    assert result.evidence_coverage_pct == 0.0
    assert result.release_allowed is False


def test_coverage_gate_blocks_release_when_expected_check_is_missing() -> None:
    result = verify_project(
        ProjectVerificationInput(
            project_id="GP-001",
            expected_check_ids=["CHECK-1", "CHECK-2"],
            checks=[
                ProjectCheckInput(
                    check_id="CHECK-1",
                    title="Completed check",
                    discipline="HVAC",
                    severity="INFO",
                    proposed_status=VerificationStatus.PASS,
                    message="Перевірку завершено.",
                    gates=[GateType.RELEASE],
                )
            ],
        )
    )

    assert result.status == VerificationStatus.HOLD
    assert result.coverage_pct == 50.0
    assert result.missing_check_ids == ["CHECK-2"]
    assert any(f.status == VerificationStatus.NOT_CHECKED for f in result.findings)
    assert result.release_allowed is False


def test_project_verify_api() -> None:
    response = client.post(
        "/verify/project",
        json={
            "project_id": "GP-API-001",
            "expected_check_ids": ["CHECK-1"],
            "checks": [
                {
                    "check_id": "CHECK-1",
                    "title": "API pass",
                    "discipline": "HVAC",
                    "severity": "INFO",
                    "proposed_status": "PASS",
                    "message": "OK",
                    "gates": ["RELEASE"],
                }
            ],
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "PASS"
    assert body["coverage_pct"] == 100.0
    assert body["release_allowed"] is True

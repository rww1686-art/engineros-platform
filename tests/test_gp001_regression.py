import json
from pathlib import Path

from app.schemas.verify import (
    EEO,
    GateType,
    ProjectCheckInput,
    ProjectVerificationInput,
    VerificationStatus,
)
from app.services.verify_kernel import verify_project

FIXTURE = Path(__file__).parent / "fixtures" / "gp001_164_04_2026_ground_truth.json"


def test_gp001_ground_truth_is_complete_and_unique() -> None:
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    findings = data["findings"]
    ids = [item["id"] for item in findings]

    assert len(findings) == data["expected_count"] == 34
    assert len(ids) == len(set(ids))
    assert "ETR-02" in ids
    assert "TX-01" in ids
    assert "SZ-04" in ids
    assert "EE-02" in ids


def test_gp001_kernel_regression_gate_reproduces_ground_truth() -> None:
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    evidence = []
    checks = []

    for item in data["findings"]:
        evidence_id = f"GP001-E-{item['id']}"
        evidence.append(
            EEO(
                evidence_id=evidence_id,
                object_id=data["project_id"],
                source_type="drawing",
                source="GP-001 audit evidence",
                locator=item["locator"],
            )
        )
        checks.append(
            ProjectCheckInput(
                check_id=item["id"],
                title=item["title"],
                discipline=item["discipline"],
                severity=item["severity"],
                proposed_status=VerificationStatus(item["status"]),
                message=f"Еталонний дефект {item['priority']}: {item['title']}",
                evidence_ids=[evidence_id],
                gates=[
                    GateType.DESIGN,
                    GateType.PROCUREMENT,
                    GateType.INSTALLATION,
                    GateType.COMMISSIONING,
                    GateType.RELEASE,
                ],
            )
        )

    result = verify_project(
        ProjectVerificationInput(
            project_id=data["project_id"],
            checks=checks,
            evidence_objects=evidence,
            expected_check_ids=[item["id"] for item in data["findings"]],
        )
    )

    actual = {finding.finding_id: finding.status.value for finding in result.findings}
    expected = {item["id"]: item["status"] for item in data["findings"]}

    assert result.coverage_pct == 100.0
    assert result.evidence_coverage_pct == 100.0
    assert result.missing_check_ids == []
    assert actual == expected
    assert result.release_allowed is False
    assert result.status == VerificationStatus.FAIL


def test_gp001_release_fails_if_one_known_check_is_omitted() -> None:
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    expected_ids = [item["id"] for item in data["findings"]]
    omitted = expected_ids[-1]

    result = verify_project(
        ProjectVerificationInput(
            project_id=data["project_id"],
            checks=[],
            evidence_objects=[],
            expected_check_ids=expected_ids,
        )
    )

    assert omitted in result.missing_check_ids
    assert result.coverage_pct == 0.0
    assert result.status == VerificationStatus.HOLD
    assert result.release_allowed is False

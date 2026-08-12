from fastapi.testclient import TestClient

from app.main import app
from app.schemas.verify import EEO, EOR, HVACVerificationInput, VerificationStatus
from app.services.verify import verify_hvac

client = TestClient(app)


def _evidence() -> list[EEO]:
    return [
        EEO(
            evidence_id="EEO-001",
            object_id="GOLD-B-001",
            source_type="calculation",
            source="heat-load-calculation.pdf",
            locator="page 12",
        ),
        EEO(
            evidence_id="EEO-002",
            object_id="GOLD-B-001",
            source_type="specification",
            source="equipment-specification.pdf",
            locator="item HP-01",
        ),
    ]


def test_verify_hvac_pass() -> None:
    payload = HVACVerificationInput(
        object=EOR(object_id="GOLD-B-001", name="Gold HVAC baseline"),
        declared_heat_load_kw=15.5,
        independent_heat_load_kw=15.0,
        equipment_capacity_kw=16.0,
        required_flow_m3_h=2.6,
        design_flow_m3_h=2.7,
        drawing_equipment_capacity_kw=16.0,
        calculation_equipment_capacity_kw=16.0,
        specification_equipment_capacity_kw=16.0,
        evidence_objects=_evidence(),
    )

    result = verify_hvac(payload)

    assert result.status == VerificationStatus.PASS
    assert result.assessed_checks == 4
    assert result.failed_checks == 0
    assert len(result.findings) == 4


def test_verify_hvac_detects_capacity_and_document_conflict() -> None:
    payload = HVACVerificationInput(
        object=EOR(object_id="GOLD-B-002", name="Conflict case"),
        declared_heat_load_kw=18.0,
        independent_heat_load_kw=18.0,
        equipment_capacity_kw=16.0,
        required_flow_m3_h=3.1,
        design_flow_m3_h=3.1,
        drawing_equipment_capacity_kw=16.0,
        calculation_equipment_capacity_kw=18.0,
        specification_equipment_capacity_kw=16.0,
        evidence_objects=_evidence(),
    )

    result = verify_hvac(payload)

    assert result.status == VerificationStatus.FAIL
    assert result.failed_checks == 2
    assert {item.finding_id for item in result.findings if item.status == VerificationStatus.FAIL} == {
        "HVAC-CAP-001",
        "HVAC-CONFLICT-001",
    }


def test_verify_hvac_reports_insufficient_data() -> None:
    result = verify_hvac(
        HVACVerificationInput(object=EOR(object_id="GOLD-B-003", name="Incomplete case"))
    )

    assert result.status == VerificationStatus.INSUFFICIENT_DATA
    assert result.assessed_checks == 0
    assert all(item.status == VerificationStatus.INSUFFICIENT_DATA for item in result.findings)


def test_verify_hvac_api() -> None:
    response = client.post(
        "/verify/hvac",
        json={
            "object": {"object_id": "GOLD-B-004", "name": "API case"},
            "declared_heat_load_kw": 15.0,
            "independent_heat_load_kw": 15.0,
            "equipment_capacity_kw": 16.0,
            "required_flow_m3_h": 2.6,
            "design_flow_m3_h": 2.6,
            "drawing_equipment_capacity_kw": 16.0,
            "calculation_equipment_capacity_kw": 16.0,
            "specification_equipment_capacity_kw": 16.0,
            "evidence_objects": [item.model_dump() for item in _evidence()],
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "PASS"
    assert response.json()["assessed_checks"] == 4

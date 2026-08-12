import json
from pathlib import Path

from app.services.real_project_state import derive_stage3_state
from app.services.stage3_gate import GateStatus, evaluate_stage3_gates

ROOT = Path(__file__).resolve().parents[1]


def _snapshot() -> dict:
    return json.loads((ROOT / "datasets/real-r12-evidence-state.json").read_text())


def test_r12_supersedes_all_previous_project_revisions() -> None:
    data = _snapshot()

    assert data["active_revision"] == 12
    assert data["supersedes"] == list(range(1, 12))
    assert data["verified"]["revision_consistency"] is True


def test_r12_manufacturer_identity_is_traceable_but_not_design_point_complete() -> None:
    data = _snapshot()
    manufacturer = next(item for item in data["sources"] if item["id"] == "SRC-GREE-UA")

    assert manufacturer["model"] == "GRS-CQ16Pd/NhG3-M"
    assert manufacturer["supply"] == "400/50/3"
    assert manufacturer["rated_heating_kw"] == 15.7
    assert manufacturer["fcu_cooling_kw"] == 13.8
    assert data["open_evidence_gaps"]["exact_minus22_w45_manufacturer_point"] is True


def test_r12_gate_state_is_derived_from_evidence_not_hardcoded() -> None:
    state = derive_stage3_state(_snapshot())
    results = {item.gate: item.status for item in evaluate_stage3_gates(state)}

    assert results["3.0 Intake completeness"] == GateStatus.PASS
    assert results["3.1 Evidence traceability"] == GateStatus.PASS
    assert results["3.2 Independent engineering calculation"] == GateStatus.INSUFFICIENT_DATA
    assert results["3.3 Equipment design-point verification"] == GateStatus.INSUFFICIENT_DATA
    assert results["3.4 Cross-document conflict detection"] == GateStatus.PASS
    assert results["3.5 Customer report integrity"] == GateStatus.PASS
    assert results["3.6 Real-project reproducibility"] == GateStatus.PASS
    assert results["3.7 Commercial readiness"] == GateStatus.INSUFFICIENT_DATA

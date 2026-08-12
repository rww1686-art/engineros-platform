import copy
import json
from pathlib import Path

from app.services.stage3_closure import evaluate_stage3_closure

ROOT = Path(__file__).resolve().parents[1]


def _snapshot() -> dict:
    return json.loads((ROOT / "datasets/real-r12-evidence-state.json").read_text())


def test_stage3_cannot_close_with_real_r12_evidence_gaps() -> None:
    decision = evaluate_stage3_closure(_snapshot())

    assert decision.can_close is False
    assert decision.open_gates == (
        "3.2 Independent engineering calculation",
        "3.3 Equipment design-point verification",
        "3.7 Commercial readiness",
    )
    assert "envelope_u_values_and_geometry" in decision.open_evidence_gaps
    assert "exact_minus22_w45_manufacturer_point" in decision.open_evidence_gaps


def test_stage3_can_close_only_after_all_evidence_and_release_holds_are_closed() -> None:
    data = copy.deepcopy(_snapshot())
    data["open_evidence_gaps"] = {
        key: False for key in data["open_evidence_gaps"]
    }
    data["release"]["procurement_hold"] = False
    data["release"]["customer_grade_release_ready"] = True

    decision = evaluate_stage3_closure(data)

    assert decision.can_close is True
    assert decision.open_gates == ()
    assert decision.open_evidence_gaps == ()

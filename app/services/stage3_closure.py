from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.services.real_project_state import derive_stage3_state
from app.services.stage3_gate import GateStatus, evaluate_stage3_gates


@dataclass(frozen=True)
class Stage3ClosureDecision:
    can_close: bool
    open_gates: tuple[str, ...]
    open_evidence_gaps: tuple[str, ...]


def evaluate_stage3_closure(snapshot: dict[str, Any]) -> Stage3ClosureDecision:
    state = derive_stage3_state(snapshot)
    gate_results = evaluate_stage3_gates(state)
    open_gates = tuple(
        result.gate for result in gate_results if result.status != GateStatus.PASS
    )

    gaps = snapshot.get("open_evidence_gaps", {})
    open_evidence_gaps = tuple(sorted(key for key, is_open in gaps.items() if is_open))

    release = snapshot.get("release", {})
    release_ready = bool(release.get("customer_grade_release_ready"))
    procurement_hold = bool(release.get("procurement_hold", True))

    can_close = (
        not open_gates
        and not open_evidence_gaps
        and release_ready
        and not procurement_hold
    )

    return Stage3ClosureDecision(
        can_close=can_close,
        open_gates=open_gates,
        open_evidence_gaps=open_evidence_gaps,
    )

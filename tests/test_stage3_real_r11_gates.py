from app.services.stage3_gate import (
    GateStatus,
    Stage3EvidenceState,
    evaluate_stage3_gates,
)


def test_historical_r11_gate_state_before_r12_evidence_upgrade() -> None:
    """Preserve the pre-R12 result; canonical current state is derived from R12 evidence."""
    state = Stage3EvidenceState(
        intake_sources_present=True,
        revision_consistency=True,
        evidence_traceability=False,
        independent_heat_load_available=False,
        exact_design_point_manufacturer_evidence=False,
        cross_document_conflicts_resolved=True,
        customer_report_integrity=True,
        reproducible=True,
        commercial_report_ready=False,
    )

    results = {item.gate: item.status for item in evaluate_stage3_gates(state)}

    assert results == {
        "3.0 Intake completeness": GateStatus.PASS,
        "3.1 Evidence traceability": GateStatus.INSUFFICIENT_DATA,
        "3.2 Independent engineering calculation": GateStatus.INSUFFICIENT_DATA,
        "3.3 Equipment design-point verification": GateStatus.INSUFFICIENT_DATA,
        "3.4 Cross-document conflict detection": GateStatus.PASS,
        "3.5 Customer report integrity": GateStatus.PASS,
        "3.6 Real-project reproducibility": GateStatus.PASS,
        "3.7 Commercial readiness": GateStatus.INSUFFICIENT_DATA,
    }

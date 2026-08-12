from dataclasses import dataclass
from enum import StrEnum


class GateStatus(StrEnum):
    PASS = "PASS"
    FAIL = "FAIL"
    INSUFFICIENT_DATA = "INSUFFICIENT DATA"


@dataclass(frozen=True)
class Stage3EvidenceState:
    intake_sources_present: bool
    revision_consistency: bool
    evidence_traceability: bool
    independent_heat_load_available: bool
    exact_design_point_manufacturer_evidence: bool
    cross_document_conflicts_resolved: bool
    customer_report_integrity: bool
    reproducible: bool
    commercial_report_ready: bool


@dataclass(frozen=True)
class GateResult:
    gate: str
    status: GateStatus
    reason: str


def evaluate_stage3_gates(state: Stage3EvidenceState) -> list[GateResult]:
    return [
        GateResult(
            "3.0 Intake completeness",
            GateStatus.PASS if state.intake_sources_present else GateStatus.INSUFFICIENT_DATA,
            "Required project sources are indexed."
            if state.intake_sources_present
            else "Required project sources are incomplete.",
        ),
        GateResult(
            "3.1 Evidence traceability",
            GateStatus.PASS if state.evidence_traceability else GateStatus.INSUFFICIENT_DATA,
            "Critical claims are traceable to project evidence."
            if state.evidence_traceability
            else "Evidence IDs/locators are incomplete for critical claims.",
        ),
        GateResult(
            "3.2 Independent engineering calculation",
            GateStatus.PASS
            if state.independent_heat_load_available
            else GateStatus.INSUFFICIENT_DATA,
            "Independent design heat-load calculation is available."
            if state.independent_heat_load_available
            else "Verified envelope and independent design heat load are absent.",
        ),
        GateResult(
            "3.3 Equipment design-point verification",
            GateStatus.PASS
            if state.exact_design_point_manufacturer_evidence
            else GateStatus.INSUFFICIENT_DATA,
            "Exact manufacturer design-point evidence is available."
            if state.exact_design_point_manufacturer_evidence
            else "Exact model variant/design-point manufacturer evidence is absent.",
        ),
        GateResult(
            "3.4 Cross-document conflict detection",
            GateStatus.PASS
            if state.revision_consistency and state.cross_document_conflicts_resolved
            else GateStatus.FAIL,
            "Revision policy applied and active cross-document conflicts resolved."
            if state.revision_consistency and state.cross_document_conflicts_resolved
            else "Active cross-document conflicts remain.",
        ),
        GateResult(
            "3.5 Customer report integrity",
            GateStatus.PASS if state.customer_report_integrity else GateStatus.FAIL,
            "Customer final status is protected by evidence readiness."
            if state.customer_report_integrity
            else "Customer report can leak an unsupported PASS.",
        ),
        GateResult(
            "3.6 Real-project reproducibility",
            GateStatus.PASS if state.reproducible else GateStatus.FAIL,
            "Recheck is deterministic."
            if state.reproducible
            else "Repeated execution is not deterministic.",
        ),
        GateResult(
            "3.7 Commercial readiness",
            GateStatus.PASS if state.commercial_report_ready else GateStatus.INSUFFICIENT_DATA,
            "Customer-grade report is ready for delivery."
            if state.commercial_report_ready
            else "Customer-grade report cannot be released until critical evidence gaps close.",
        ),
    ]

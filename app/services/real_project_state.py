from __future__ import annotations

from typing import Any

from app.services.stage3_gate import Stage3EvidenceState


def derive_stage3_state(snapshot: dict[str, Any]) -> Stage3EvidenceState:
    sources = snapshot.get("sources", [])
    verified = snapshot.get("verified", {})
    gaps = snapshot.get("open_evidence_gaps", {})
    release = snapshot.get("release", {})

    intake_sources_present = bool(sources) and all(
        bool(source.get("traceable")) for source in sources
    )
    evidence_traceability = bool(verified.get("evidence_traceability"))
    independent_heat_load_available = not bool(
        gaps.get("independent_final_heat_load", True)
    )
    exact_design_point_manufacturer_evidence = not bool(
        gaps.get("exact_minus22_w45_manufacturer_point", True)
    )

    return Stage3EvidenceState(
        intake_sources_present=intake_sources_present,
        revision_consistency=bool(verified.get("revision_consistency")),
        evidence_traceability=evidence_traceability,
        independent_heat_load_available=independent_heat_load_available,
        exact_design_point_manufacturer_evidence=exact_design_point_manufacturer_evidence,
        cross_document_conflicts_resolved=bool(verified.get("revision_consistency")),
        customer_report_integrity=bool(release.get("customer_report_integrity")),
        reproducible=bool(release.get("reproducible")),
        commercial_report_ready=bool(release.get("customer_grade_release_ready")),
    )

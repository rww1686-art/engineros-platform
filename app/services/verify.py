from app.schemas.verify import (
    Finding,
    HVACVerificationInput,
    HVACVerificationResult,
    VerificationStatus,
)

HEAT_LOAD_TOLERANCE_PCT = 10.0
FLOW_TOLERANCE_PCT = 10.0
CAPACITY_MARGIN_MIN_PCT = 0.0
CONFLICT_TOLERANCE_PCT = 2.0


def _evidence_ids(payload: HVACVerificationInput) -> list[str]:
    return [item.evidence_id for item in payload.evidence_objects]


def _difference_pct(reference: float, actual: float) -> float:
    return abs(actual - reference) / reference * 100.0


def _finding(
    finding_id: str,
    check: str,
    status: VerificationStatus,
    severity: str,
    message: str,
    evidence_ids: list[str],
    metrics: dict[str, float | str] | None = None,
) -> Finding:
    return Finding(
        finding_id=finding_id,
        check=check,
        status=status,
        severity=severity,  # type: ignore[arg-type]
        message=message,
        evidence_ids=evidence_ids,
        metrics=metrics or {},
    )


def verify_hvac(payload: HVACVerificationInput) -> HVACVerificationResult:
    evidence_ids = _evidence_ids(payload)
    findings: list[Finding] = []

    if payload.declared_heat_load_kw is None or payload.independent_heat_load_kw is None:
        findings.append(
            _finding(
                "HVAC-LOAD-001",
                "Heating Load Verification",
                VerificationStatus.INSUFFICIENT_DATA,
                "MEDIUM",
                "Declared and independent heating loads are required for verification.",
                evidence_ids,
            )
        )
    else:
        deviation = _difference_pct(payload.independent_heat_load_kw, payload.declared_heat_load_kw)
        load_status = (
            VerificationStatus.PASS
            if deviation <= HEAT_LOAD_TOLERANCE_PCT
            else VerificationStatus.REVIEW_REQUIRED
        )
        findings.append(
            _finding(
                "HVAC-LOAD-001",
                "Heating Load Verification",
                load_status,
                "INFO" if load_status == VerificationStatus.PASS else "HIGH",
                f"Heating-load deviation is {deviation:.1f}%.",
                evidence_ids,
                {"deviation_pct": round(deviation, 2)},
            )
        )

    required_capacity = payload.independent_heat_load_kw or payload.declared_heat_load_kw
    if required_capacity is None or payload.equipment_capacity_kw is None:
        findings.append(
            _finding(
                "HVAC-CAP-001",
                "Equipment Capacity Verification",
                VerificationStatus.INSUFFICIENT_DATA,
                "MEDIUM",
                "Required load and equipment capacity are required for verification.",
                evidence_ids,
            )
        )
    else:
        margin = (payload.equipment_capacity_kw - required_capacity) / required_capacity * 100.0
        capacity_status = (
            VerificationStatus.PASS
            if margin >= CAPACITY_MARGIN_MIN_PCT
            else VerificationStatus.FAIL
        )
        findings.append(
            _finding(
                "HVAC-CAP-001",
                "Equipment Capacity Verification",
                capacity_status,
                "INFO" if capacity_status == VerificationStatus.PASS else "CRITICAL",
                f"Equipment capacity margin is {margin:.1f}%.",
                evidence_ids,
                {"capacity_margin_pct": round(margin, 2)},
            )
        )

    if payload.required_flow_m3_h is None or payload.design_flow_m3_h is None:
        findings.append(
            _finding(
                "HVAC-HYD-001",
                "Hydraulic Consistency Verification",
                VerificationStatus.INSUFFICIENT_DATA,
                "MEDIUM",
                "Required and design flow rates are required for hydraulic verification.",
                evidence_ids,
            )
        )
    else:
        flow_deviation = _difference_pct(payload.required_flow_m3_h, payload.design_flow_m3_h)
        hydraulic_status = (
            VerificationStatus.PASS
            if flow_deviation <= FLOW_TOLERANCE_PCT
            else VerificationStatus.REVIEW_REQUIRED
        )
        findings.append(
            _finding(
                "HVAC-HYD-001",
                "Hydraulic Consistency Verification",
                hydraulic_status,
                "INFO" if hydraulic_status == VerificationStatus.PASS else "HIGH",
                f"Design-flow deviation is {flow_deviation:.1f}%.",
                evidence_ids,
                {"flow_deviation_pct": round(flow_deviation, 2)},
            )
        )

    source_values = {
        "drawing": payload.drawing_equipment_capacity_kw,
        "calculation": payload.calculation_equipment_capacity_kw,
        "specification": payload.specification_equipment_capacity_kw,
    }
    available = {name: value for name, value in source_values.items() if value is not None}
    if len(available) < 2:
        findings.append(
            _finding(
                "HVAC-CONFLICT-001",
                "Drawing ↔ Calculation ↔ Specification Conflict Detection",
                VerificationStatus.INSUFFICIENT_DATA,
                "MEDIUM",
                "At least two source values are required for conflict detection.",
                evidence_ids,
            )
        )
    else:
        values = list(available.values())
        minimum = min(values)
        maximum = max(values)
        conflict = _difference_pct(minimum, maximum) if minimum > 0 else 100.0
        conflict_status = (
            VerificationStatus.PASS
            if conflict <= CONFLICT_TOLERANCE_PCT
            else VerificationStatus.FAIL
        )
        findings.append(
            _finding(
                "HVAC-CONFLICT-001",
                "Drawing ↔ Calculation ↔ Specification Conflict Detection",
                conflict_status,
                "INFO" if conflict_status == VerificationStatus.PASS else "HIGH",
                f"Cross-document equipment-capacity spread is {conflict:.1f}%.",
                evidence_ids,
                {"source_spread_pct": round(conflict, 2)},
            )
        )

    assessed = [item for item in findings if item.status != VerificationStatus.INSUFFICIENT_DATA]
    failed = [
        item
        for item in findings
        if item.status in {VerificationStatus.FAIL, VerificationStatus.REVIEW_REQUIRED}
    ]
    insufficient = [
        item for item in findings if item.status == VerificationStatus.INSUFFICIENT_DATA
    ]
    if any(item.status == VerificationStatus.FAIL for item in findings):
        overall = VerificationStatus.FAIL
    elif any(item.status == VerificationStatus.REVIEW_REQUIRED for item in findings):
        overall = VerificationStatus.REVIEW_REQUIRED
    elif insufficient:
        overall = VerificationStatus.INSUFFICIENT_DATA
    else:
        overall = VerificationStatus.PASS

    return HVACVerificationResult(
        object_id=payload.object.object_id,
        status=overall,
        findings=findings,
        assessed_checks=len(assessed),
        failed_checks=len(failed),
    )

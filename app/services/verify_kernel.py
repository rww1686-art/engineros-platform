from collections import defaultdict

from app.schemas.verify import (
    Finding,
    GateResult,
    GateType,
    ProjectVerificationInput,
    ProjectVerificationResult,
    VerificationStatus,
)

BLOCKING_STATUSES = {VerificationStatus.FAIL, VerificationStatus.HOLD}
CRITICAL_SEVERITIES = {"HIGH", "CRITICAL"}


def _critic_status(check, known_evidence: set[str]) -> VerificationStatus:
    """Adversarial evidence firewall.

    A critical FAIL is only allowed when at least one referenced evidence object
    exists in the submitted evidence registry. Unsupported critical claims are
    downgraded to HOLD instead of being presented as proven defects.
    """
    if not check.applicable:
        return VerificationStatus.NOT_APPLICABLE

    if check.proposed_status == VerificationStatus.FAIL and check.severity in CRITICAL_SEVERITIES:
        if not set(check.evidence_ids) & known_evidence:
            return VerificationStatus.HOLD

    return check.proposed_status


def verify_project(payload: ProjectVerificationInput) -> ProjectVerificationResult:
    """Run the R8 project-level verification kernel.

    Invariants:
    - every supplied check is processed; an early P0/FAIL never short-circuits;
    - HIGH/CRITICAL FAIL requires registered evidence;
    - expected checks that were not supplied are explicitly NOT CHECKED;
    - project release is blocked by FAIL/HOLD or incomplete coverage;
    - gate decisions are derived from canonical findings, not report prose.
    """
    evidence_ids = {item.evidence_id for item in payload.evidence_objects}
    findings: list[Finding] = []
    supplied_ids: set[str] = set()
    evidence_required = 0
    evidence_satisfied = 0

    for check in payload.checks:
        supplied_ids.add(check.check_id)
        status = _critic_status(check, evidence_ids)
        valid_evidence = [eid for eid in check.evidence_ids if eid in evidence_ids]

        if check.severity in CRITICAL_SEVERITIES and status in BLOCKING_STATUSES:
            evidence_required += 1
            if valid_evidence:
                evidence_satisfied += 1

        findings.append(
            Finding(
                finding_id=check.check_id,
                check=check.title,
                status=status,
                severity=check.severity,
                message=check.message,
                evidence_ids=valid_evidence,
                metrics={"discipline": check.discipline},
            )
        )

    expected = set(payload.expected_check_ids)
    missing = sorted(expected - supplied_ids)
    for check_id in missing:
        findings.append(
            Finding(
                finding_id=check_id,
                check="Очікувана перевірка не виконана",
                status=VerificationStatus.NOT_CHECKED,
                severity="MEDIUM",
                message="Перевірка передбачена матрицею покриття, але результат не надано.",
                evidence_ids=[],
                metrics={},
            )
        )

    planned = len(expected) if expected else len(payload.checks)
    completed = len(expected & supplied_ids) if expected else len(payload.checks)
    coverage = round((completed / planned * 100.0), 2) if planned else 0.0
    evidence_coverage = (
        round(evidence_satisfied / evidence_required * 100.0, 2)
        if evidence_required
        else 100.0
    )

    by_gate: dict[GateType, list[str]] = defaultdict(list)
    check_by_id = {item.check_id: item for item in payload.checks}
    finding_by_id = {item.finding_id: item for item in findings}

    for check_id, check in check_by_id.items():
        finding = finding_by_id[check_id]
        if finding.status in BLOCKING_STATUSES:
            for gate in check.gates:
                by_gate[gate].append(check_id)

    gates: list[GateResult] = []
    for gate in GateType:
        blockers = sorted(by_gate.get(gate, []))
        if blockers:
            gate_status = VerificationStatus.HOLD
        elif coverage < 100.0:
            gate_status = VerificationStatus.HOLD
        else:
            gate_status = VerificationStatus.PASS
        gates.append(GateResult(gate=gate, status=gate_status, blocking_findings=blockers))

    failed = sum(item.status == VerificationStatus.FAIL for item in findings)
    holds = sum(item.status == VerificationStatus.HOLD for item in findings)

    if failed:
        overall = VerificationStatus.FAIL
    elif holds or missing or coverage < 100.0:
        overall = VerificationStatus.HOLD
    elif any(item.status == VerificationStatus.REVIEW_REQUIRED for item in findings):
        overall = VerificationStatus.REVIEW_REQUIRED
    else:
        overall = VerificationStatus.PASS

    release_gate = next(item for item in gates if item.gate == GateType.RELEASE)
    release_allowed = overall == VerificationStatus.PASS and release_gate.status == VerificationStatus.PASS

    return ProjectVerificationResult(
        project_id=payload.project_id,
        status=overall,
        findings=findings,
        gates=gates,
        planned_checks=planned,
        completed_checks=completed,
        coverage_pct=coverage,
        failed_checks=failed,
        hold_checks=holds,
        missing_check_ids=missing,
        evidence_coverage_pct=evidence_coverage,
        release_allowed=release_allowed,
    )

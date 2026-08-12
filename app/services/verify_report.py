from app.schemas.verify import HVACVerificationResult
from app.services.customer_readiness import CustomerGradeReadinessResult


def _findings_lines(result: HVACVerificationResult) -> list[str]:
    lines: list[str] = []
    for finding in result.findings:
        lines.extend(
            [
                f"### {finding.finding_id} — {finding.check}",
                f"Status: **{finding.status.value}**",
                f"Severity: **{finding.severity}**",
                finding.message,
                "Evidence: "
                + (", ".join(f"`{item}`" for item in finding.evidence_ids) or "none"),
                "",
            ]
        )
    return lines


def render_verification_report(result: HVACVerificationResult) -> str:
    """Render an internal/core verification report.

    This renderer is not a customer-grade release decision. Use
    ``render_customer_verification_report`` for client-facing output.
    """
    lines = [
        "# ENGINEROS VERIFY — HVAC PROJECT AUDIT (CORE)",
        "",
        f"Object: `{result.object_id}`",
        f"Core verification status: **{result.status.value}**",
        f"Assessed checks: {result.assessed_checks}",
        f"Failed/review checks: {result.failed_checks}",
        "",
        "## Findings",
        "",
    ]
    lines.extend(_findings_lines(result))
    lines.extend(
        [
            "## Evidence policy",
            "",
            "NO CRITICAL CLAIM WITHOUT EVIDENCE.",
            "",
            "This is a core verification result, not a customer-grade release decision.",
        ]
    )
    return "\n".join(lines)


def render_customer_verification_report(
    result: HVACVerificationResult,
    readiness: CustomerGradeReadinessResult,
) -> str:
    """Render a client-facing report using the final evidence-readiness status."""
    lines = [
        "# ENGINEROS VERIFY — HVAC PROJECT AUDIT",
        "",
        f"Object: `{result.object_id}`",
        f"Final customer status: **{readiness.status.value}**",
        f"Core verification status: **{result.status.value}**",
        f"Customer-grade: **{'YES' if readiness.customer_grade else 'NO'}**",
        f"Release decision: {readiness.reason}",
        f"Evidence source: `{readiness.source_id}`" if readiness.source_id else "Evidence source: none",
        f"Assessed checks: {result.assessed_checks}",
        f"Failed/review checks: {result.failed_checks}",
        "",
        "## Findings",
        "",
    ]
    lines.extend(_findings_lines(result))
    lines.extend(
        [
            "## Evidence policy",
            "",
            "NO CRITICAL CLAIM WITHOUT EVIDENCE.",
            "",
            "The final customer status is controlled by the evidence-readiness gate.",
            "Controlled synthetic data must not be represented as customer evidence.",
        ]
    )
    return "\n".join(lines)

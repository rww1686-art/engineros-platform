from app.schemas.verify import HVACVerificationResult


def render_verification_report(result: HVACVerificationResult) -> str:
    lines = [
        "# ENGINEROS VERIFY — HVAC PROJECT AUDIT",
        "",
        f"Object: `{result.object_id}`",
        f"Overall status: **{result.status.value}**",
        f"Assessed checks: {result.assessed_checks}",
        f"Failed/review checks: {result.failed_checks}",
        "",
        "## Findings",
        "",
    ]

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

    lines.extend(
        [
            "## Evidence policy",
            "",
            "NO CRITICAL CLAIM WITHOUT EVIDENCE.",
            "",
            "This report is generated from the provided structured engineering dataset. ",
            "Controlled synthetic datasets must not be represented as customer evidence.",
        ]
    )
    return "\n".join(lines)

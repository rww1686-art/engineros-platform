from dataclasses import dataclass


@dataclass(frozen=True)
class ManufacturerEvidencePoint:
    outdoor_temp_c: float
    leaving_water_temp_c: float
    capacity_kw: float
    source_id: str


@dataclass(frozen=True)
class DesignPointEvidenceResult:
    covered: bool
    source_id: str | None
    capacity_kw: float | None
    reason: str


def verify_design_point_evidence(
    *,
    points: list[ManufacturerEvidencePoint],
    outdoor_temp_c: float,
    leaving_water_temp_c: float,
) -> DesignPointEvidenceResult:
    matches = [
        point
        for point in points
        if point.outdoor_temp_c == outdoor_temp_c
        and point.leaving_water_temp_c == leaving_water_temp_c
    ]
    if len(matches) == 1:
        point = matches[0]
        return DesignPointEvidenceResult(
            covered=True,
            source_id=point.source_id,
            capacity_kw=point.capacity_kw,
            reason="Exact manufacturer evidence point is available.",
        )
    if len(matches) > 1:
        return DesignPointEvidenceResult(
            covered=False,
            source_id=None,
            capacity_kw=None,
            reason="Multiple manufacturer evidence points match the requested design point.",
        )
    return DesignPointEvidenceResult(
        covered=False,
        source_id=None,
        capacity_kw=None,
        reason=(
            "No exact manufacturer evidence point is available "
            "for the requested design condition."
        ),
    )

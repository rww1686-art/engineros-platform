from dataclasses import dataclass

DESIGN_POINT_TOLERANCE_C = 0.01


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


def _same_temperature(actual: float, expected: float) -> bool:
    return abs(actual - expected) <= DESIGN_POINT_TOLERANCE_C


def verify_design_point_evidence(
    *,
    points: list[ManufacturerEvidencePoint],
    outdoor_temp_c: float,
    leaving_water_temp_c: float,
) -> DesignPointEvidenceResult:
    matches = [
        point
        for point in points
        if _same_temperature(point.outdoor_temp_c, outdoor_temp_c)
        and _same_temperature(point.leaving_water_temp_c, leaving_water_temp_c)
    ]
    if len(matches) == 1:
        point = matches[0]
        if point.capacity_kw <= 0:
            return DesignPointEvidenceResult(
                covered=False,
                source_id=None,
                capacity_kw=None,
                reason="Manufacturer evidence capacity must be positive.",
            )
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

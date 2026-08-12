from dataclasses import dataclass


@dataclass(frozen=True)
class PerformancePoint:
    outdoor_temp_c: float
    leaving_water_temp_c: float
    capacity_kw: float


@dataclass(frozen=True)
class EquipmentCapacityResult:
    design_capacity_kw: float
    required_load_kw: float
    margin_kw: float
    margin_pct: float
    sufficient: bool


def verify_design_point_capacity(
    *,
    performance_points: list[PerformancePoint],
    outdoor_temp_c: float,
    leaving_water_temp_c: float,
    required_load_kw: float,
) -> EquipmentCapacityResult:
    if required_load_kw <= 0:
        raise ValueError("required_load_kw must be positive")

    matching = [
        point
        for point in performance_points
        if point.outdoor_temp_c == outdoor_temp_c
        and point.leaving_water_temp_c == leaving_water_temp_c
    ]
    if len(matching) != 1:
        raise ValueError("exactly one matching design performance point is required")

    capacity = matching[0].capacity_kw
    margin_kw = capacity - required_load_kw
    margin_pct = margin_kw / required_load_kw * 100.0
    return EquipmentCapacityResult(
        design_capacity_kw=round(capacity, 3),
        required_load_kw=round(required_load_kw, 3),
        margin_kw=round(margin_kw, 3),
        margin_pct=round(margin_pct, 2),
        sufficient=margin_kw >= 0,
    )

from dataclasses import dataclass

WATER_HEAT_CAPACITY_FACTOR = 1.163


@dataclass(frozen=True)
class HydraulicFlowResult:
    heat_load_kw: float
    delta_t_k: float
    required_flow_m3_h: float


def calculate_required_water_flow(*, heat_load_kw: float, delta_t_k: float) -> HydraulicFlowResult:
    if heat_load_kw <= 0:
        raise ValueError("heat_load_kw must be positive")
    if delta_t_k <= 0:
        raise ValueError("delta_t_k must be positive")

    flow = heat_load_kw / (WATER_HEAT_CAPACITY_FACTOR * delta_t_k)
    return HydraulicFlowResult(
        heat_load_kw=round(heat_load_kw, 3),
        delta_t_k=round(delta_t_k, 3),
        required_flow_m3_h=round(flow, 3),
    )

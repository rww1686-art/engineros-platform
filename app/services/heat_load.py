from dataclasses import dataclass


@dataclass(frozen=True)
class EnvelopeElement:
    area_m2: float
    u_w_m2k: float


@dataclass(frozen=True)
class HeatLoadResult:
    transmission_kw: float
    ventilation_kw: float
    total_heat_loss_kw: float


def calculate_design_heat_load(
    *,
    elements: list[EnvelopeElement],
    delta_t_k: float,
    heated_volume_m3: float,
    air_changes_per_hour: float,
    heat_recovery_efficiency: float = 0.0,
) -> HeatLoadResult:
    if delta_t_k <= 0:
        raise ValueError("delta_t_k must be positive")
    if heated_volume_m3 <= 0:
        raise ValueError("heated_volume_m3 must be positive")
    if air_changes_per_hour < 0:
        raise ValueError("air_changes_per_hour must be non-negative")
    if not 0.0 <= heat_recovery_efficiency < 1.0:
        raise ValueError("heat_recovery_efficiency must be in [0, 1)")

    transmission_w = sum(item.area_m2 * item.u_w_m2k for item in elements) * delta_t_k
    ventilation_w = (
        0.33
        * air_changes_per_hour
        * heated_volume_m3
        * delta_t_k
        * (1.0 - heat_recovery_efficiency)
    )

    transmission_kw = transmission_w / 1000.0
    ventilation_kw = ventilation_w / 1000.0
    return HeatLoadResult(
        transmission_kw=round(transmission_kw, 3),
        ventilation_kw=round(ventilation_kw, 3),
        total_heat_loss_kw=round(transmission_kw + ventilation_kw, 3),
    )

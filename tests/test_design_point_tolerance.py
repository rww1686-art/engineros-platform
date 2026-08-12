import pytest

from app.services.equipment_performance import PerformancePoint, verify_design_point_capacity
from app.services.evidence_gate import ManufacturerEvidencePoint, verify_design_point_evidence


def test_equipment_performance_accepts_numeric_noise_within_tolerance() -> None:
    result = verify_design_point_capacity(
        performance_points=[
            PerformancePoint(
                outdoor_temp_c=-20.0001,
                leaving_water_temp_c=45.0001,
                capacity_kw=15.0,
            )
        ],
        outdoor_temp_c=-20.0,
        leaving_water_temp_c=45.0,
        required_load_kw=14.8,
    )

    assert result.sufficient is True
    assert result.design_capacity_kw == 15.0


def test_manufacturer_evidence_accepts_numeric_noise_within_tolerance() -> None:
    result = verify_design_point_evidence(
        points=[
            ManufacturerEvidencePoint(
                outdoor_temp_c=-20.0001,
                leaving_water_temp_c=45.0001,
                capacity_kw=15.0,
                source_id="EEO-001",
            )
        ],
        outdoor_temp_c=-20.0,
        leaving_water_temp_c=45.0,
    )

    assert result.covered is True
    assert result.source_id == "EEO-001"


def test_invalid_non_positive_performance_capacity_is_rejected() -> None:
    with pytest.raises(ValueError, match="capacity must be positive"):
        verify_design_point_capacity(
            performance_points=[
                PerformancePoint(
                    outdoor_temp_c=-20.0,
                    leaving_water_temp_c=45.0,
                    capacity_kw=0.0,
                )
            ],
            outdoor_temp_c=-20.0,
            leaving_water_temp_c=45.0,
            required_load_kw=14.8,
        )


def test_invalid_manufacturer_capacity_is_not_covered() -> None:
    result = verify_design_point_evidence(
        points=[
            ManufacturerEvidencePoint(
                outdoor_temp_c=-20.0,
                leaving_water_temp_c=45.0,
                capacity_kw=0.0,
                source_id="EEO-BAD",
            )
        ],
        outdoor_temp_c=-20.0,
        leaving_water_temp_c=45.0,
    )

    assert result.covered is False
    assert result.capacity_kw is None

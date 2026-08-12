from app.services.evidence_gate import ManufacturerEvidencePoint, verify_design_point_evidence


def test_nominal_gree_point_does_not_cover_minus20_w45() -> None:
    points = [
        ManufacturerEvidencePoint(
            outdoor_temp_c=7.0,
            leaving_water_temp_c=35.0,
            capacity_kw=15.5,
            source_id="EEO-GREE-V3-16-001",
        )
    ]

    result = verify_design_point_evidence(
        points=points,
        outdoor_temp_c=-20.0,
        leaving_water_temp_c=45.0,
    )

    assert result.covered is False
    assert result.capacity_kw is None
    assert "No exact manufacturer evidence point" in result.reason


def test_exact_manufacturer_point_is_accepted() -> None:
    points = [
        ManufacturerEvidencePoint(
            outdoor_temp_c=-20.0,
            leaving_water_temp_c=45.0,
            capacity_kw=14.8,
            source_id="EEO-MANUFACTURER-DESIGN-POINT",
        )
    ]

    result = verify_design_point_evidence(
        points=points,
        outdoor_temp_c=-20.0,
        leaving_water_temp_c=45.0,
    )

    assert result.covered is True
    assert result.capacity_kw == 14.8
    assert result.source_id == "EEO-MANUFACTURER-DESIGN-POINT"

import json
from pathlib import Path

from app.schemas.verify import HVACVerificationInput, VerificationStatus
from app.services.equipment_performance import PerformancePoint, verify_design_point_capacity
from app.services.hydraulics import calculate_required_water_flow
from app.services.verify import verify_hvac
from app.services.verify_report import render_verification_report

ROOT = Path(__file__).resolve().parents[1]


def test_gold_b_001_design_point_hydraulics_and_report() -> None:
    payload_data = json.loads((ROOT / "datasets/gold-b-001.json").read_text())
    performance = json.loads(
        (ROOT / "datasets/gold-b-001-equipment-performance.json").read_text()
    )

    points = [PerformancePoint(**item) for item in performance["performance_points"]]
    capacity = verify_design_point_capacity(
        performance_points=points,
        outdoor_temp_c=-20.0,
        leaving_water_temp_c=45.0,
        required_load_kw=payload_data["independent_heat_load_kw"],
    )
    assert capacity.design_capacity_kw == 15.6
    assert capacity.sufficient is True
    assert capacity.margin_pct > 0

    hydraulic = calculate_required_water_flow(
        heat_load_kw=payload_data["independent_heat_load_kw"],
        delta_t_k=5.0,
    )
    assert hydraulic.required_flow_m3_h == 2.609
    assert abs(payload_data["required_flow_m3_h"] - hydraulic.required_flow_m3_h) <= 0.01

    verification = verify_hvac(HVACVerificationInput.model_validate(payload_data))
    assert verification.status == VerificationStatus.PASS

    report = render_verification_report(verification)
    assert "ENGINEROS VERIFY" in report
    assert "Overall status: **PASS**" in report
    assert "HVAC-LOAD-001" in report
    assert "NO CRITICAL CLAIM WITHOUT EVIDENCE" in report

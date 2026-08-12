import json
from pathlib import Path

from app.schemas.verify import HVACVerificationInput, VerificationStatus
from app.services.heat_load import EnvelopeElement, calculate_design_heat_load
from app.services.verify import verify_hvac

ROOT = Path(__file__).resolve().parents[1]


def test_gold_b_001_independent_heat_load_and_verify_flow() -> None:
    envelope = json.loads((ROOT / "datasets/gold-b-001-envelope.json").read_text())
    payload_data = json.loads((ROOT / "datasets/gold-b-001.json").read_text())

    elements = [
        EnvelopeElement(area_m2=item["area_m2"], u_w_m2k=item["u_w_m2k"])
        for item in envelope["elements"]
    ]
    result = calculate_design_heat_load(
        elements=elements,
        delta_t_k=envelope["design"]["delta_t_k"],
        heated_volume_m3=envelope["design"]["heated_volume_m3"],
        air_changes_per_hour=envelope["ventilation"]["air_changes_per_hour"],
        heat_recovery_efficiency=envelope["ventilation"]["heat_recovery_efficiency"],
    )

    assert result.transmission_kw == 5.867
    assert result.ventilation_kw == 9.305
    assert result.total_heat_loss_kw == 15.173
    assert abs(payload_data["independent_heat_load_kw"] - result.total_heat_loss_kw) <= 0.05

    verification = verify_hvac(HVACVerificationInput.model_validate(payload_data))
    assert verification.status == VerificationStatus.PASS
    assert verification.assessed_checks == 4
    assert verification.failed_checks == 0

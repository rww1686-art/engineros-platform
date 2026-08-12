import json
from pathlib import Path

from app.services.project_consistency import (
    ProjectValue,
    apply_revision_policy,
    find_active_conflicts,
)

ROOT = Path(__file__).resolve().parents[1]


def _load_values() -> tuple[int, list[ProjectValue]]:
    data = json.loads((ROOT / "datasets/real-r11-project-values.json").read_text())
    values = [ProjectValue(**item) for item in data["values"]]
    return data["active_revision"], values


def test_r11_primary_check_detects_cross_revision_conflicts() -> None:
    _, values = _load_values()
    conflicts = find_active_conflicts(values)

    assert {item.key for item in conflicts} == {
        "buffer_volume_l",
        "fcu_cooling_capacity_each_kw",
        "fcu_water_flow_each_m3_h",
    }


def test_r11_recheck_is_clean_after_revision_policy() -> None:
    active_revision, values = _load_values()
    corrected = apply_revision_policy(values, active_revision)
    conflicts = find_active_conflicts(corrected)

    assert conflicts == []
    assert all(
        item.active is (item.revision == active_revision)
        for item in corrected
    )

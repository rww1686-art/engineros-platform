from dataclasses import dataclass


@dataclass(frozen=True)
class ProjectValue:
    key: str
    value: float | str
    source_id: str
    revision: int
    unit: str | None = None
    active: bool = True


@dataclass(frozen=True)
class ProjectConflict:
    key: str
    source_ids: tuple[str, ...]
    values: tuple[float | str, ...]


def find_active_conflicts(values: list[ProjectValue]) -> list[ProjectConflict]:
    grouped: dict[str, list[ProjectValue]] = {}
    for item in values:
        if item.active:
            grouped.setdefault(item.key, []).append(item)

    conflicts: list[ProjectConflict] = []
    for key, items in grouped.items():
        normalized = {str(item.value).strip().casefold() for item in items}
        if len(normalized) > 1:
            conflicts.append(
                ProjectConflict(
                    key=key,
                    source_ids=tuple(item.source_id for item in items),
                    values=tuple(item.value for item in items),
                )
            )
    return conflicts


def apply_revision_policy(values: list[ProjectValue], active_revision: int) -> list[ProjectValue]:
    """Deactivate project records older than the explicitly active revision."""
    return [
        ProjectValue(
            key=item.key,
            value=item.value,
            source_id=item.source_id,
            revision=item.revision,
            unit=item.unit,
            active=item.revision == active_revision,
        )
        for item in values
    ]

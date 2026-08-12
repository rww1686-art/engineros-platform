from enum import StrEnum
from typing import Annotated, Literal

from pydantic import BaseModel, Field, model_validator

PositiveFloat = Annotated[float, Field(gt=0)]
NonNegativeFloat = Annotated[float, Field(ge=0)]


class VerificationStatus(StrEnum):
    PASS = "PASS"
    PASS_WITH_CONDITIONS = "PASS WITH CONDITIONS"
    REVIEW_REQUIRED = "REVIEW REQUIRED"
    FAIL = "FAIL"
    HOLD = "HOLD"
    INSUFFICIENT_DATA = "INSUFFICIENT DATA"
    NOT_ASSESSED = "NOT ASSESSED"
    NOT_CHECKED = "NOT CHECKED"
    NOT_APPLICABLE = "N/A"


class GateType(StrEnum):
    DESIGN = "DESIGN"
    PROCUREMENT = "PROCUREMENT"
    INSTALLATION = "INSTALLATION"
    COMMISSIONING = "COMMISSIONING"
    RELEASE = "RELEASE"


class EvidenceRef(BaseModel):
    evidence_id: str = Field(min_length=1, max_length=100)
    source: str = Field(min_length=1, max_length=255)
    locator: str | None = Field(default=None, max_length=500)
    note: str | None = Field(default=None, max_length=1000)


class EOR(BaseModel):
    """Engineering Object Record: verified project/object context."""

    object_id: str = Field(min_length=1, max_length=100)
    name: str = Field(min_length=1, max_length=255)
    discipline: Literal["HVAC"] = "HVAC"
    design_outdoor_temp_c: float | None = None
    design_indoor_temp_c: float | None = None
    heated_area_m2: PositiveFloat | None = None
    evidence: list[EvidenceRef] = Field(default_factory=list)


class EFO(BaseModel):
    """Engineering Fact Object: normalized engineering fact with provenance."""

    fact_id: str = Field(min_length=1, max_length=100)
    object_id: str = Field(min_length=1, max_length=100)
    fact_type: str = Field(min_length=1, max_length=100)
    value: float | str | bool
    unit: str | None = Field(default=None, max_length=32)
    evidence: list[EvidenceRef] = Field(min_length=1)


class EDO(BaseModel):
    """Engineering Decision Object: design selection or declared engineering decision."""

    decision_id: str = Field(min_length=1, max_length=100)
    object_id: str = Field(min_length=1, max_length=100)
    decision_type: str = Field(min_length=1, max_length=100)
    selected_value: float | str | bool
    unit: str | None = Field(default=None, max_length=32)
    evidence: list[EvidenceRef] = Field(default_factory=list)


class EEO(BaseModel):
    """Engineering Evidence Object: immutable evidence descriptor used by VERIFY."""

    evidence_id: str = Field(min_length=1, max_length=100)
    object_id: str = Field(min_length=1, max_length=100)
    source_type: Literal["drawing", "calculation", "specification", "datasheet", "input"]
    source: str = Field(min_length=1, max_length=255)
    locator: str | None = Field(default=None, max_length=500)
    content_hash: str | None = Field(default=None, max_length=128)


class HVACVerificationInput(BaseModel):
    object: EOR
    declared_heat_load_kw: PositiveFloat | None = None
    independent_heat_load_kw: PositiveFloat | None = None
    equipment_capacity_kw: PositiveFloat | None = None
    design_flow_m3_h: PositiveFloat | None = None
    required_flow_m3_h: PositiveFloat | None = None
    drawing_equipment_capacity_kw: PositiveFloat | None = None
    calculation_equipment_capacity_kw: PositiveFloat | None = None
    specification_equipment_capacity_kw: PositiveFloat | None = None
    facts: list[EFO] = Field(default_factory=list)
    decisions: list[EDO] = Field(default_factory=list)
    evidence_objects: list[EEO] = Field(default_factory=list)


class Finding(BaseModel):
    finding_id: str
    check: str
    status: VerificationStatus
    severity: Literal["INFO", "LOW", "MEDIUM", "HIGH", "CRITICAL"]
    message: str
    evidence_ids: list[str] = Field(default_factory=list)
    metrics: dict[str, float | str] = Field(default_factory=dict)

    @model_validator(mode="after")
    def critical_claim_requires_evidence(self) -> "Finding":
        critical_failure = (
            self.severity in {"HIGH", "CRITICAL"}
            and self.status == VerificationStatus.FAIL
        )
        if critical_failure and not self.evidence_ids:
            raise ValueError("HIGH/CRITICAL FAIL requires evidence")
        return self


class HVACVerificationResult(BaseModel):
    object_id: str
    status: VerificationStatus
    findings: list[Finding]
    assessed_checks: int
    failed_checks: int


class ProjectCheckInput(BaseModel):
    """Canonical input for one independent verification check."""

    check_id: str = Field(min_length=1, max_length=120)
    title: str = Field(min_length=1, max_length=255)
    discipline: str = Field(min_length=1, max_length=64)
    severity: Literal["INFO", "LOW", "MEDIUM", "HIGH", "CRITICAL"]
    proposed_status: VerificationStatus
    message: str = Field(min_length=1, max_length=2000)
    evidence_ids: list[str] = Field(default_factory=list)
    gates: list[GateType] = Field(default_factory=list)
    applicable: bool = True


class ProjectVerificationInput(BaseModel):
    project_id: str = Field(min_length=1, max_length=120)
    checks: list[ProjectCheckInput] = Field(default_factory=list)
    evidence_objects: list[EEO] = Field(default_factory=list)
    expected_check_ids: list[str] = Field(default_factory=list)


class GateResult(BaseModel):
    gate: GateType
    status: VerificationStatus
    blocking_findings: list[str] = Field(default_factory=list)


class ProjectVerificationResult(BaseModel):
    project_id: str
    status: VerificationStatus
    findings: list[Finding]
    gates: list[GateResult]
    planned_checks: int
    completed_checks: int
    coverage_pct: float
    failed_checks: int
    hold_checks: int
    missing_check_ids: list[str] = Field(default_factory=list)
    evidence_coverage_pct: float
    release_allowed: bool

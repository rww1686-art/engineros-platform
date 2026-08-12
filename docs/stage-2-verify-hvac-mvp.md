# Етап 2 — ENGINEROS VERIFY / HVAC MVP

## Мета

Перетворити ENGINEROS з базової EIP-платформи на executable engineering verification product, який приймає структуровані дані HVAC-проєкту та повертає findings із доказами.

## P0 scope

1. Heating Load Verification.
2. Equipment Capacity Verification.
3. Hydraulic Consistency Verification.
4. Drawing ↔ Calculation ↔ Specification Conflict Detection.

## Канонічні об’єкти

- `EOR` — Engineering Object Record: контекст об’єкта/проєкту.
- `EFO` — Engineering Fact Object: нормалізований інженерний факт із provenance.
- `EDO` — Engineering Decision Object: проєктне рішення або вибір.
- `EEO` — Engineering Evidence Object: доказ, на який може посилатися finding.

## Статуси

`PASS`, `PASS WITH CONDITIONS`, `REVIEW REQUIRED`, `FAIL`, `INSUFFICIENT DATA`, `NOT ASSESSED`.

## Критичне правило

**NO CRITICAL CLAIM WITHOUT EVIDENCE.**

HIGH/CRITICAL finding не може бути сформований без `evidence_ids`. Це правило реалізоване на рівні Pydantic schema.

## Перший executable flow

`POST /verify/hvac`

Input → canonical objects → deterministic P0 checks → findings → overall status.

На першому кроці engine є детермінованим і не використовує LLM для інженерного висновку. Це забезпечує відтворюваність та тестованість базового Kernel.

## Поточні thresholds MVP-0

- Heating-load deviation: PASS ≤ 10%.
- Hydraulic design-flow deviation: PASS ≤ 10%.
- Equipment capacity: FAIL, якщо capacity < verified/declared required load.
- Cross-document equipment capacity spread: PASS ≤ 2%, інакше FAIL.

Thresholds є version-0 policy і мають бути замінені/розширені перевіреними engineering rulesets та нормативними/виробничими datasets.

## Acceptance Gate 2.1

- canonical schemas існують;
- `/verify/hvac` існує в OpenAPI;
- 4 P0 checks executable;
- PASS case покритий тестом;
- FAIL/conflict case покритий тестом;
- insufficient-data case покритий тестом;
- HIGH/CRITICAL findings потребують evidence;
- CI green.

## Наступний gate

GOLD-B-001: повний envelope dataset → незалежний heat-load calculation → equipment performance map → hydraulic check → drawing/calculation/specification conflict detection → verified client-facing report.

# ENGINEROS — ЕТАП 3: REAL PROJECT VALIDATION / CUSTOMER VERIFY

## Статус
ACTIVE

## Мета
Перевести ENGINEROS VERIFY / HVAC з контрольованого MVP-0 у customer-grade validation на реальному HVAC-проєкті з повним evidence trail.

## Операційний цикл
REAL PROJECT → INGEST → NORMALIZE → VERIFY → FINDINGS → EVIDENCE → CUSTOMER REPORT → ENGINEER REVIEW → PAID VALIDATION

## P0 scope
1. Heating Load Verification.
2. Equipment Capacity Verification.
3. Hydraulic Consistency Verification.
4. Drawing ↔ Calculation ↔ Specification Conflict Detection.
5. Manufacturer design-point evidence gate.
6. Customer-grade report gate.

## Обов’язкові вхідні дані першого реального проєкту
- креслення HVAC;
- теплотехнічний/теплотехнічні розрахунки або вихідні дані для незалежного розрахунку;
- специфікація обладнання;
- паспорт/selection data виробника;
- design outdoor / indoor temperatures;
- температурний графік системи;
- розрахункова теплова потужність;
- розрахункові витрати теплоносія;
- ідентифіковані джерела доказів з locator/hash;
- реєстр EOR/EFO/EDO/EEO.

## Acceptance gates
### Gate 3.0 — Intake completeness
PASS, якщо усі обов’язкові джерела отримані або пропуски явно класифіковані як INSUFFICIENT DATA.

### Gate 3.1 — Evidence traceability
PASS, якщо кожне HIGH/CRITICAL твердження має EEO/evidence ID і джерело, яке можна відтворити.

### Gate 3.2 — Independent engineering calculation
PASS, якщо ENGINEROS може незалежно відтворити ключові теплові/гідравлічні величини та показати deviation.

### Gate 3.3 — Equipment design-point verification
PASS, якщо є traceable manufacturer evidence для фактичної design point. Заборонено підміняти nominal/rated data точкою, якої виробник не підтверджує.

### Gate 3.4 — Cross-document conflict detection
PASS, якщо drawing/calculation/specification зіставлені на object/segment level і всі конфлікти сформовані як findings.

### Gate 3.5 — Customer report integrity
PASS, якщо final customer status визначається readiness/evidence gate, а не лише core verification status.

### Gate 3.6 — Real-project reproducibility
PASS, якщо повторний прогін того самого dataset дає детермінований результат.

### Gate 3.7 — Commercial readiness
PASS, якщо сформовано customer-grade report, engineer review checklist, перелік обмежень і матеріал придатний до передачі замовнику.

## STOP RULE
Етап 3 не закривається на synthetic-only evidence. Потрібен щонайменше один реальний HVAC-проєкт із документально підтверджуваним evidence trail.

## Exit criteria
Етап 3 закрито тільки якщо:
- усі Gate 3.0–3.7 = PASS;
- немає відкритих P0 дефектів;
- перший real-project dataset прогнано end-to-end;
- customer-grade final report сформовано без evidence leakage;
- результат придатний для першої платної/комерційної валідації.

## Наступний після Етапу 3 формат
PAID PROJECT VALIDATION → 10 PAID PROJECTS → STRUCTURED DATA CAPTURE → AUTOMATION → SCALE.

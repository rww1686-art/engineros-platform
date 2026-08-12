# ENGINEROS VERIFY — Етап 3 / REAL-R12-001

## Поточний статус

**R12 повторно перевірено після усунення міжревізійних дефектів. Stage 3 НЕ ЗАКРИТО.**

Причина незакриття — не дефект Kernel, а відсутні первинні інженерні докази, які не можна замінити припущеннями.

## Контроль ревізій

- Активна ревізія: `R12`.
- `R12` замінює `R11` і попередні R1–R10.
- Застарілі значення R9/R11 не допускаються до active verification після застосування revision policy.
- Буфер: 300 л, 4-патрубковий.
- FCU: 2 × не менше 12 кВт при 7/12 °C.
- Розрахункова витрата одного FCU: 2.064 м³/год при 12 кВт і ΔT=5 K.
- HP-2 не фіксується як 10 кВт без доказової performance map; модель TBD.

## Manufacturer evidence HP-1

Підтверджена модельна модифікація R12: `GREE Versati IV GRS-CQ16Pd/NhG3-M`, 400 V / 50 Hz / 3 Ph.

Контрольні підтверджені дані:
- nominal heating class: 15.7 кВт;
- FCU cooling rating: 13.8 кВт;
- наявний окремий контрольний benchmark A−20/W45: 7.27 кВт.

**Заборонено:** переносити A−20/W45 на A−22/W45 або використовувати номінальні 15.7 кВт як морозову потужність.

## Що було виправлено

1. Стару R9/R11 специфікацію вилучено з active truth set.
2. Буфер 100–200 л → 300 л.
3. FCU 6.3 кВт → критерій ≥12 кВт кожний.
4. FCU 1.29 м³/год → 2.064 м³/год кожний для 12 кВт / ΔT=5 K.
5. HP-2 «10 кВт» → MODEL TBD із підбором за фактичним дефіцитом.
6. HP-1 зафіксований на трифазній модифікації G3-M, але фактичний паспорт/шильда поставки лишається acceptance evidence.
7. Gate state тепер обчислюється з evidence snapshot, а не задається вручну у тесті.
8. Доданий Stage 3 Closure Guard: етап неможливо закрити, доки є відкритий critical evidence gap, procurement HOLD або хоча б один Gate не PASS.

## Результат повторної перевірки до фінального Gate

- Revision consistency: PASS.
- Cross-document active conflicts: PASS / 0 active conflicts після revision policy.
- Evidence source registry: PASS.
- Customer-report evidence protection: PASS.
- Reproducibility: PASS.

## Реальні незакриті evidence gaps

1. Точна адреса об’єкта та підтверджена розрахункова температура зовнішнього повітря.
2. Склад огороджень, U-значення та верифікована геометрія для повного незалежного heat-load calculation.
3. Final independent heat load після закриття envelope.
4. Exact manufacturer performance evidence HP-1 для фактичної design point; для поточного R12 це A−22/W45, якщо −22 °C буде підтверджено.
5. Точна модель газового котла та його доступна теплова потужність у проєктному режимі.
6. Точні моделі FCU, performance/ESP/noise/Δp tables.
7. Manufacturer output радіаторів при фактичному низькотемпературному режимі 45/35 °C.

## Gate state після R12 evidence upgrade

- Gate 3.0 Intake completeness — PASS.
- Gate 3.1 Evidence traceability — PASS.
- Gate 3.2 Independent engineering calculation — INSUFFICIENT DATA.
- Gate 3.3 Equipment design-point verification — INSUFFICIENT DATA.
- Gate 3.4 Cross-document conflict detection — PASS.
- Gate 3.5 Customer report integrity — PASS.
- Gate 3.6 Real-project reproducibility — PASS.
- Gate 3.7 Commercial readiness — INSUFFICIENT DATA.

## Рішення

**Stage 3 closure: BLOCKED BY EVIDENCE.**

ENGINEROS не повинен переводити цей проєкт у customer-grade PASS або закупівельний RELEASE шляхом підстановки припущень. Наступний прогін Gate виконується після отримання/підтвердження первинних даних для Gate 3.2 і 3.3 та формування фінального customer-grade report для Gate 3.7.

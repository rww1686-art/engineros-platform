# Етап 2 — Manufacturer Evidence Gate

## Мета

Заборонити ENGINEROS робити висновок про достатність теплового насоса в розрахунковій точці без точного, трасованого performance evidence виробника.

## Поточний перевірений факт GREE Versati III 16 kW

Офіційний каталог GREE Ukraine для моделі `GRSCQ16PdG/NhH2-E` підтверджує номінальну теплову потужність 15.5 кВт за опублікованою рейтинговою умовою опалення: зовнішнє повітря 7°C DB / 6°C WB, вода 30/35°C. Джерело також підтверджує робочий діапазон зовнішньої температури в режимі опалення -25…35°C та діапазон температури теплоносія 20…60°C.

Ці дані **не є доказом** потужності в точці `-20°C / W45`.

## Правило Kernel

- exact manufacturer point для design condition → evidence coverage PASS;
- лише nominal/rating point на інших температурах → design-point evidence INSUFFICIENT;
- synthetic/interpolated performance map не може використовуватися як commercial critical evidence;
- критичний висновок щодо Equipment Capacity Verification дозволяється лише після exact або формально дозволеної validated interpolation policy з трасованим manufacturer dataset.

## Поточний статус GOLD-B-001

GOLD-B-001 залишається контрольним synthetic baseline для перевірки Kernel. Manufacturer evidence додано окремо та не змішується із synthetic performance map. До отримання точного GREE performance point для `-20°C / W45` customer-grade висновок щодо потужності в цій точці має статус `INSUFFICIENT DATA / REVIEW REQUIRED`, а не PASS.

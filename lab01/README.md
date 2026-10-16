# Лабораторна робота №1. Основи функціонального програмування у Python

**Варіант 13 — страхові поліси.** Вхідні дані: базова премія, рівень ризику, стаж клієнта, активність полісу. Для активних полісів обчислюється кінцева страхова премія: `base_premium × коефіцієнт ризику × (1 − знижка за стаж)`.
Виконав: Маньківський Максим Володимирович, ФЕП-23.

## Цілі

- зрозуміти, що таке чиста функція і референтна прозорість;
- виявити та ізолювати побічні ефекти (print, глобальна таблиця `RISK_RATES`, мутація вхідних словників);
- переписати імперативний фрагмент `starter_imperative.py` у функціональному стилі;
- параметризувати обчислення через `typing.Callable`.

## Що зроблено

| Файл | Призначення |
|---|---|
| `core.py` | Чисте ядро варіанта 13: `final_premium`, `with_premium`, `make_policy_processor` (фабрика обробника), `process_policies_pure`, фабрики політик `min_premium_filter` / `table_risk` / `years_discount`; додаткові вправи `compose`, `pipe`, `make_multiplier`, `stamp_total` (інжекція годинника); базове завдання з методички: `order_subtotal`, `with_total`, `make_processor(accept, apply_discount, apply_tax)`, `process_orders_pure`. Жодного I/O, глобалів і мутацій. |
| `app.py` | Оболонка побічних ефектів: читання полісів із JSON, `render_report`, `run` (базове завдання), `print`, `time.time`. |
| `starter_imperative.py` | Початковий імперативний код (`process_orders` з методички та `process_policies` за варіантом) — лишений для тестів еквівалентності. |
| `tests/test_core.py` | pytest для варіанта 13: референтна прозорість, відсутність мутацій, збіг з імперативною версією, Callable-політики, `compose`, `make_multiplier`, `stamp_total`, `render_report`. |
| `tests/test_orders.py` | pytest для базового завдання (замовлення): мінімальні тести з методички. |
| `tests/test_properties.py` | property-based тести (Hypothesis): референтна прозорість, відсутність мутацій, інваріанти підсумку. |
| `conftest.py` | Фікстури `sample_policies`, `sample_orders`. |

Політики передаються як `Callable[[float], bool]` (фільтр за базовою премією), `Callable[[str], float]`
(коефіцієнт ризику) та `Callable[[int], float]` (знижка за стаж);
`make_policy_processor(accept=..., risk_factor=..., loyalty_discount=...)` повертає налаштований обробник
`Callable[[Iterable[Policy]], Report]`. `process_policies_pure` — окремий випадок, зібраний із фабрик політик.

## Як запускати

```bash
pip install -r requirements.txt
python app.py              # вбудований приклад
python app.py policies.json  # поліси з файлу (список об'єктів {id, base_premium, risk, years, active})

pytest
mypy .
ruff check .
black --check .
```

Усі команди виконуються з каталогу `lab01/`.

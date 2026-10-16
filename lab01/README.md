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
| `core.py` | Чисте ядро: `final_premium`, `with_premium`, `make_processor` (фабрика обробника), `process_policies_pure`, фабрики політик `min_premium_filter` / `table_risk` / `years_discount`, `compose`, `make_multiplier`, `stamp_total` (інжекція годинника). Жодного I/O, глобалів і мутацій. |
| `app.py` | Оболонка побічних ефектів: читання полісів із JSON, `render_report`, `print`, `time.time`. |
| `starter_imperative.py` | Початковий імперативний код із завдання — лишений для тесту еквівалентності. |
| `tests/test_core.py` | pytest: референтна прозорість, відсутність мутацій, збіг з імперативною версією, Callable-політики, `compose`, `make_multiplier`, `stamp_total`, `render_report`. |
| `conftest.py` | Фікстура `sample_policies`. |

Політики передаються як `Callable[[float], bool]` (фільтр за базовою премією), `Callable[[str], float]`
(коефіцієнт ризику) та `Callable[[int], float]` (знижка за стаж);
`make_processor(accept=..., risk_factor=..., loyalty_discount=...)` повертає налаштований обробник
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

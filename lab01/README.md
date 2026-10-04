# Лабораторна робота №1. Основи функціонального програмування у Python

**Варіант 1 — обробка замовлень інтернет-магазину.**
Виконав: Маньківський Максим Володимирович, ФЕП-23с.

## Цілі

- зрозуміти, що таке чиста функція і референтна прозорість;
- виявити та ізолювати побічні ефекти (print, глобальний `TAX_RATE`, мутація вхідних словників);
- переписати імперативний фрагмент `starter_imperative.py` у функціональному стилі;
- параметризувати обчислення через `typing.Callable`.

## Що зроблено

| Файл | Призначення |
|---|---|
| `core.py` | Чисте ядро: `order_subtotal`, `with_total`, `make_processor` (фабрика обробника), `process_orders_pure`, фабрики політик `min_total_filter` / `percent_discount` / `flat_tax`, `compose`, `make_multiplier`, `stamp_total` (інжекція годинника). Жодного I/O, глобалів і мутацій. |
| `app.py` | Оболонка побічних ефектів: читання замовлень із JSON, `render_report`, `print`, `time.time`. |
| `starter_imperative.py` | Початковий імперативний код із завдання — лишений для тесту еквівалентності. |
| `tests/test_core.py` | pytest: референтна прозорість, відсутність мутацій, збіг з імперативною версією, Callable-політики, `compose`, `make_multiplier`, `stamp_total`, `render_report`. |
| `conftest.py` | Фікстура `sample_orders`. |

Політики передаються як `Callable[[float], bool]` (фільтр), `Callable[[float], float]` (знижка, податок);
`make_processor(accept=..., apply_discount=..., apply_tax=...)` повертає налаштований обробник
`Callable[[Iterable[Order]], Report]`. `process_orders_pure` — окремий випадок, зібраний із фабрик політик.

## Як запускати

```bash
pip install -r requirements.txt
python app.py              # вбудований приклад
python app.py orders.json  # замовлення з файлу (список об'єктів {id, items:[{price, qty}], paid})

pytest
mypy .
ruff check .
black --check .
```

Усі команди виконуються з каталогу `lab01/`.

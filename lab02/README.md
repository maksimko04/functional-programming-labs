# Лабораторна робота №2. Функції вищого порядку, lambda, композиція

**Варіант 13 — доставка посилок.** Запис: `id`, `sender`, `region`, `delivery_parts` (частини вартості).
Конвеєр: вартість доставки = сума частин → регіональний коефіцієнт → фільтр за порогом →
сортування (вартість спадно, `id` зростом) → Top-N. Reduce-агрегація: `count`, `delivery_sum`, `avg_delivery`.
Виконав: Маньківський Максим Володимирович, ФЕП-23.

## Цілі

- map / filter / reduce та їх генераторні еквіваленти;
- функції вищого порядку і `lambda`;
- композиція функцій (`compose`, `pipe`, `juxt`) і збирання конвеєра без проміжних змінних;
- жодних мутацій вхідних записів — кожен крок повертає нові словники.

## Що зроблено

| Файл | Призначення |
|---|---|
| `core.py` | Чисте ядро. Композиція: `compose`, `pipe`, `juxt`. Варіант 13: `Parcel` (TypedDict), трансформації `with_cost` (map), `boost_region` (map), `min_cost` (filter), `normalize_senders` (map), `sort_by_cost_desc` (два ключі), `take` (islice), агрегація `reduce_delivery_stats`, збирання `build_delivery_pipeline`. Базовий приклад з методички (клієнти: `only_adults`, `with_total`, `boost_city`, `normalize_names`, `sort_by_total_desc`, `take_records`, `reduce_stats`, `build_pipeline`). |
| `app.py` | Оболонка I/O та CLI (argparse): читання JSON, рендер і друк результату. |
| `sample_data.json` | Приклад вхідних даних. |
| `tests/test_core.py` | pytest: Top-N і тай-брейкер, відсутність мутацій, фільтр за порогом, reduce-агрегація, еквівалентність композиції ручному ланцюжку, `pipe`/`juxt`, базовий конвеєр. |
| `tests/test_properties.py` | Hypothesis: Top-N є префіксом повного відсортованого списку, відсутність мутацій, узгодженість статистик. |
| `conftest.py` | Фікстури `parcels`, `records`. |

Кожна трансформація — фабрика, що повертає функцію `Iterable[Parcel] -> Iterable[Parcel]`,
тому конвеєр збирається через `compose(...)` з однотипних кроків. `lambda` використано у
фільтрі, map-кроках і ключі сортування.

## Як запускати

```bash
pip install -r requirements.txt
python app.py --top 3 --boost-region West --factor 1.2 --min-cost 50
python app.py --data sample_data.json --top 2

pytest
mypy .
ruff check .
black --check .
```

Усі команди виконуються з каталогу `lab02/`.

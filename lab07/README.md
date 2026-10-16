# Лабораторна робота №7. functools та operator

**Варіант 13 — мобільні тарифні плани.** Запис: `name`, `minutes`, `data_gb`, `sms`, `price`.
Конвеєр: нормалізація → фільтр за вимогами користувача → розрахунок `score` (зважена корисність
на одиницю ціни) → сортування (`score` ↓, `price` ↑, `name` ↑) → Top-N.
Виконав: Маньківський Максим Володимирович, ФЕП-23.

## Цілі

- `functools.partial` для часткового застосування та побудови конвеєрів;
- `functools.reduce` як універсальний `pipeline(value, *funcs)` і для агрегації;
- `operator.itemgetter` / `attrgetter` / `methodcaller` замість lambda-гетерів;
- поліморфний API завантаження даних через `functools.singledispatch`;
- повний порядок доменного класу через `functools.total_ordering`.

## Що зроблено

| Файл | Призначення |
|---|---|
| `core.py` | `pipeline` через `reduce`; `mapf`/`filt` як `partial(map/filter)`; трансформації тарифів `normalize_tariff` (`itemgetter`, `methodcaller`), `meets_requirements` і `score` (параметризуються через `partial`), `with_score`, `to_tariff`; `rank_tariffs` збирає конвеєр, сортує `attrgetter`-ключами за кількома критеріями та бере Top-N; `total_price` — reduce-агрегація. Базовий приклад з методички: `clean_and_rank` для студентів. |
| `models.py` | `Tariff` — frozen dataclass з `@total_ordering`: `__eq__`/`__lt__` за `(score, -price, name)`, `NotImplemented` для чужих типів. |
| `loaders.py` | `@singledispatch load_tariffs` для JSON-рядка, шляху `str`, `pathlib.Path` (.json/.csv), відкритого текстового файлу та готового списку словників; `load_users` — той самий loader для базового прикладу. |
| `main.py` | Демо: завантаження з трьох джерел, Top-3 за вимогами з аргументів, сума цін. |
| `sample_data.json`, `sample_data.csv` | Приклади даних. |
| `tests/test_lab07.py` | pytest: pipeline, partial, operator, конвеєр і Top-N, відсутність мутацій, усі джерела `singledispatch`, помилкові входи, усі оператори порівняння `Tariff`, базовий приклад. |
| `tests/test_properties.py` | Hypothesis: Top-N є префіксом відсортованого результату, відсутність мутацій, фільтр за `min_minutes`. |

## Як запускати

```bash
pip install -r requirements.txt
python main.py                 # вимоги за замовчуванням: 300 хв, 10 ГБ, 0 sms
python main.py 500 20 100      # min_minutes min_data min_sms

pytest
mypy --strict .
ruff check .
black --check .
```

Усі команди виконуються з каталогу `lab07/`.

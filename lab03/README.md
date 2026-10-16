# Лабораторна робота №3. Нездатні до змін структури даних (immutability)

**Варіант 13 — страхові поліси.** Сутності `Policy` і `Coverage`, ризики як `frozenset`,
метадані клієнта як `MappingProxyType`. Pure-оновлення: додавання покриття, додавання ризику,
перерахунок премії; один розрахунок (`final_premium`) кешується через `lru_cache`.
Виконав: Маньківський Максим Володимирович, ФЕП-23.

## Цілі

- застосувати `tuple`, `frozenset`, `@dataclass(frozen=True, slots=True)`, `MappingProxyType`;
- замінити мутації на повернення нових копій (`dataclasses.replace`, конкатенація tuple, `|` для frozenset);
- перевірити немутацію, read-only поведінку та хешованість тестами;
- виміряти ефект переходу на незмінну модель (`pytest --durations=5`).

## Що зроблено

| Файл | Призначення |
|---|---|
| `model.py` | `Coverage`, `Policy` (frozen, slots), `Risk = Literal[...]`, `make_meta` (proxy над копією), `make_policy`. Методи `add_coverage` / `add_risk` / `deactivate` повертають нові об'єкти через `replace`. |
| `core.py` | Чисті функції: `risk_factor`, `final_premium` (`@lru_cache`), pure-оновлення `add_coverage`, `add_risk`, `with_meta`, `recalculate`, `index_by_policy` (поліс як ключ словника), `freeze` (глибоке заморожування). |
| `mutable_model.py` | Мутабельна версія «до» (dict + list + set) — лише для порівняння часу. |
| `main.py` | Демонстрація: ланцюжок оновлень, незмінність оригіналу, кеш, read-only meta. |
| `tests/test_immutability.py` | Немутація, `FrozenInstanceError`, `TypeError` для proxy, копіювання джерела meta, хешованість і словник з ключем-полісом, кеш `cache_info`, `freeze`, 2 property-тести (Hypothesis). |
| `tests/test_performance.py` | Два тести однакового навантаження на mutable- і immutable-моделі для `--durations=5`. |
| `conftest.py` | Фікстура `policy`. |

### Хешованість

`Policy` хешований завдяки `frozen=True`, але поле `meta` (`mappingproxy`) не має `__hash__`,
тому воно виключене з хешу через `field(hash=False)` і бере участь лише у `__eq__`. Усі інші
поля (`tuple`, `frozenset`, примітиви) хешуються.

## Порівняння часу (`python -m pytest -q --durations=5`)

| Тест | Модель | Час |
|---|---|---|
| `test_mutable_before` | dict + list + set, премія щоразу перераховується | ~0.23 s |
| `test_immutable_after` | frozen dataclass + tuple + `lru_cache` | ~0.01 s |

Незмінна модель на 2000 додаваннях покриттів створює 2000 нових tuple (O(n²) копіювання), але
кешований розрахунок премії повністю компенсує це: 1999 звернень із 2000 — cache hit.

## Висновок про незмінність

Переваги: референтна прозорість і прості тести без `deepcopy`, безпечне спільне читання,
хешованість (поліс як ключ `dict`, вхід `lru_cache`). Накладні витрати: кожне оновлення
створює новий об'єкт і копіює tuple/frozenset, `MappingProxyType` захищає лише верхній рівень
(для вкладених структур потрібен `freeze`). Для доменних сутностей розміру «поліс» ці витрати
несуттєві, а виграш у передбачуваності — великий.

## Як запускати

```bash
pip install -r requirements.txt
python main.py

pytest -q --durations=5
mypy .
ruff check .
black --check .
```

Усі команди виконуються з каталогу `lab03/`.

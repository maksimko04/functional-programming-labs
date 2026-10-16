# Функціональне програмування на Python — лабораторні роботи

Маньківський Максим Володимирович, ФЕП-23, варіант 13.

| Лабораторна | Тема | Варіант 13 |
|---|---|---|
| [lab01](lab01/) | Основи ФП: чисті функції, референтна прозорість, `typing.Callable` | Страхові поліси |
| [lab02](lab02/) | Функції вищого порядку, lambda, композиція: конвеєр map/filter/reduce | Доставка посилок |
| [lab03](lab03/) | Незмінні структури даних: tuple, frozenset, frozen dataclass, MappingProxyType | Страхові поліси |
| [lab04](lab04/) | Рекурсія та мемоізація: quicksort, обходи дерев, lru_cache | Паліндроми |
| [lab05](lab05/) | Ліниві обчислення: генератори та itertools | Ковзні максимуми |
| [lab06](lab06/) | Замикання та декоратори як HOF | Контроль доступу за токеном |
| [lab07](lab07/) | functools та operator: partial, reduce, singledispatch, total_ordering | Мобільні тарифні плани |
| [lab08](lab08/) | Алгебраїчні типи даних: Union, Literal, Protocol, match/case | Платіжні операції |

Кожна `labN/` — самостійний проєкт: `README.md`, код, `tests/` (pytest + Hypothesis),
`requirements.txt` і звіт `report.pdf`. Стиль: `black`, `ruff`; типи: `mypy --strict`
(конфіг у `pyproject.toml`).

## Як запускати

Команди виконуються з каталогу конкретної лабораторної (модулі різних лаб мають
однакові імена, тому запуск pytest/mypy з кореня репозиторію не підтримується):

```bash
cd lab03
pip install -r requirements.txt
pytest -q
mypy --strict .
ruff check .
black --check .
```

Усі лаби одразу: `python check_all.py` з кореня репозиторію.

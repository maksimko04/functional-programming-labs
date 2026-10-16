# Лабораторна робота №5. Ліниві обчислення: генератори та itertools

**Варіант 13 — ковзні максимуми.** Потік числових спостережень (можливо нескінченний,
значення постачає інжектований `Callable`), для вікна `k` ліниво обчислюються
максимум, мінімум і розмах; береться лише перші `N` результатів через `islice`.
Виконав: Маньківський Максим Володимирович, ФЕП-23.

## Цілі

- generator expressions, `yield` / `yield from`, ітератори та лінивість;
- робота з нескінченними послідовностями (`fib_stream`, `naturals`, `observations`);
- `itertools`: `islice`, `count`, `cycle`, `accumulate`, `takewhile`, `dropwhile`, `starmap`;
- універсальні `take` / `drop` / `sliding_window` та статистика по вікнах.

## Що зроблено

| Файл | Призначення |
|---|---|
| `streams.py` | Базове з методички: `fib_stream`, `naturals`, `take`, `drop`, `sliding_window` (на `deque(maxlen=k)`), `moving_average`, `window_sums` (`starmap`), обгортки `prefix_sums` / `prefix_products` (`accumulate`), `take_while` / `drop_while`. |
| `observations.py` | Варіант 13: нескінченний генератор `observations(provider)`, ковзні `window_max` / `window_min` / `window_range`, `window_stats` (NamedTuple `WindowStats`), `first_n_stats` з `islice`. |
| `main.py` | Демо: Фібоначчі, вікна натуральних, рухоме середнє, ковзна статистика по циклічному потоку. |
| `tests/test_fib_stream.py` | Перші 10 значень, `drop` + `take`, свіжий генератор на кожен виклик. |
| `tests/test_take_drop.py` | Просування спільного ітератора, `count`, `n = 0`, порожнє джерело, `n < 0`. |
| `tests/test_sliding_window.py` | Базові й граничні вікна (`k > len`, порожнє джерело, `k <= 0`), суми та рухоме середнє. |
| `tests/test_accumulate.py` | `accumulate` із сумою / добутком / `max`, `takewhile` / `dropwhile` на `count`. |
| `tests/test_window_stats.py` | Max / min / range, нескінченний потік, граничні випадки, 3 property-тести Hypothesis. |
| `tests/test_laziness.py` | Ітератор-лічильник: обчислюється рівно стільки елементів, скільки запитано. |

## Лінивість і нескінченні потоки

Жодна функція ядра не викликає `list()` на вході: `sliding_window` тримає лише `k`
останніх елементів у `deque`, `window_max` — це `map(max, ...)` над вікнами, `observations`
викликає постачальника тільки тоді, коли споживач просить наступне значення. Тому
`window_max(observations(sensor), 3)` над нескінченним потоком безпечний — доки конвеєр
завершується `islice` / `take` / `takewhile`. Єдина матеріалізація — `take` і `first_n_stats`
на виході. `drop(n, it)` промотує `n` елементів одразу при виклику (як у методичці).

## Як запускати

```bash
pip install -r requirements.txt
python main.py

pytest
mypy .
ruff check .
black --check .
```

Усі команди виконуються з каталогу `lab05/`.

# Лабораторна робота №6. Замикання та декоратори як HOF

**Варіант 13 — декоратор контролю доступу за токеном.** Замикання зберігає множину
допустимих токенів, `@authorized(verify)` перевіряє токен перед виконанням захищеної
функції через інжектований сервіс перевірки, а нестабільний сервіс обгорнуто у `@retries`.
Виконав: Маньківський Максим Володимирович, ФЕП-23.

## Цілі

- замикання, що утримують стан (`nonlocal`) і залежності;
- параметризовані декоратори як фабрики декораторів, `functools.wraps`;
- типізація обгорток через `ParamSpec`, `TypeVar`, `Concatenate`, `Protocol`;
- інжекція `clock` / `sleep` / `logger` / `time_fn` / `verify`, щоб тести були детермінованими.

## Що зроблено

| Файл | Призначення |
|---|---|
| `closures.py` | `make_counter` (стан через `nonlocal`), `make_logger(prefix, sink)`, `make_token_registry` (замикання над `frozenset` токенів), `make_revocable_registry` (пара `verify` / `revoke` над спільним станом). |
| `decorators.py` | `timed(label, unit, logger, clock)` — лог часу у `finally`; `retries(attempts, exceptions, delay, backoff, jitter, sleep, logger, rand)` — експоненційний бекоф; `cached(ttl, time_fn)` — TTL-кеш з `cache_clear` / `cache_invalidate(predicate)` / `cache_size` (типізовано через `Protocol` `CachedFn` + `cast`); `authorized(verify, logger)` — варіант 13, токен першим позиційним аргументом (`Concatenate[str, P]`), власний `AuthError`. |
| `app.py` | Демо: нестабільний `remote_verify` під `@retries`, захищена `account_balance` = `timed(authorized(cached(compute_balance)))`; `sleep` і `clock` підмінені. |
| `tests/test_closures.py` | Стан лічильника, незалежність замикань, логер із sink, реєстри токенів, 2 property-тести. |
| `tests/test_timed.py` | Фейковий годинник і логер, лог при винятку, одиниці виміру, `__name__` / `__doc__` / `__wrapped__`. |
| `tests/test_retries.py` | Успіх на 3-й спробі без сну, повторне підняття винятку, лише вказані винятки, детермінований джиттер, `attempts < 1`. |
| `tests/test_cached.py` | TTL фейковим часом, точкова та повна інвалідація, метадані, property-тест «кожен аргумент обчислено один раз». |
| `tests/test_authorized.py` | Валідний / порожній / чужий токен, повідомлення помилок, сервіс перевірки з ретраями, порядок декораторів. |

## Порядок застосування декораторів

Декоратори застосовуються знизу вгору, тож у `app.py`:

```python
account_balance = timed(...)(authorized(remote_verify)(cached(...)(compute_balance)))
```

виклик проходить `timed → authorized → cached → функція`. Кеш лежить **усередині**
авторизації: повторний виклик із валідним токеном бере значення з кешу (функція не
обчислюється вдруге), але невалідний токен відхиляється до звернення в кеш, а `timed`
логує кожен виклик, включно з відмовами. Якби `cached` стояв зовні, кеш-хіт обійшов би
перевірку токена.

## Як запускати

```bash
pip install -r requirements.txt
python app.py

pytest
mypy .
ruff check .
black --check .
```

Усі команди виконуються з каталогу `lab06/`; жоден тест не викликає реальний `sleep`.

# Лабораторна робота №8. Алгебраїчні типи даних «по-Python'івськи»

**Варіант 13 — платіжні операції.** ADT `Payment = CardPayment | BankTransfer | CashPayment | Batch`,
валюти через `Literal["UAH", "USD", "EUR"]`, структурний контракт `PaymentSource` через `Protocol`,
чисті функції `fee`, `total_with_fee`, `statistics`, `describe` через `match/case`.
Виконав: Маньківський Максим Володимирович, ФЕП-23.

## Модель

| Вузол | Поля |
|---|---|
| `CardPayment` | `amount`, `currency`, `network: Literal["visa","mastercard"]`, `last4` |
| `BankTransfer` | `amount`, `currency`, `iban`, `urgent` |
| `CashPayment` | `amount`, `currency` |
| `Batch` | `items: tuple[Payment, ...]`, `label` — рекурсивний вузол, пакет може містити пакети |

Усі вузли — `@dataclass(frozen=True)`: хешовані, незмінні; функції повертають нові значення.

## Що зроблено

| Файл | Призначення |
|---|---|
| `model.py` | ADT, `TypeAlias` `Payment`, `Literal` `Currency`/`CardNetwork`, `Protocol` `PaymentSource`. |
| `evaluator.py` | `fee` (visa 2 %, mastercard 1.8 %, переказ 5 + 10 за терміновість, готівка 0), `convert` за явною таблицею курсів, `total_with_fee` (рекурсивно для `Batch`), `kind`, `flatten`, `statistics`, `currency_of`. Від'ємна сума → `ValueError`, невідома валюта → `KeyError`. |
| `pretty.py` | `describe` — рекурсивний текстовий опис із відступами; `Protocol` `Renders`. |
| `expr.py`, `eval_.py` | Базове завдання з методички: `Expr = Num \| Add \| Mul`, `eval_expr` з `EvalOverflow`, `render`, альтернативний `Bin` з `Literal["+", "*"]`. |
| `main.py` | Демонстраційний запуск. |
| `tests/test_payments.py` | pytest: комісії, рекурсивні суми, конвертація, помилкові входи, незмінність і хешованість, `flatten`/`statistics`, рендер вкладеного пакета, `Protocol`. |
| `tests/test_expr.py` | Тести базового завдання, зокрема переповнення. |
| `tests/test_properties.py` | Hypothesis: рекурсивні пакети — сума пакета дорівнює сумі листків; статистика узгоджена; рендер виразу обчислюється до того ж значення. |
| `mypy.ini` | Строгий режим mypy. |

## Як запускати

```bash
pip install -r requirements.txt
python main.py

pytest
mypy --strict .
ruff check .
black --check .
```

Усі команди виконуються з каталогу `lab08/`.

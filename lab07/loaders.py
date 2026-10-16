"""Поліморфне завантаження даних через functools.singledispatch (ЛР7)."""

from __future__ import annotations

import csv
import io
import json
from collections.abc import Mapping
from functools import singledispatch
from pathlib import Path
from typing import Any

Rows = list[dict[str, Any]]


def _parse_text(text: str) -> Rows:
    """JSON, якщо текст починається з '[', інакше CSV."""
    stripped = text.strip()
    if stripped.startswith("["):
        return _check(json.loads(stripped))
    return list(csv.DictReader(io.StringIO(stripped)))


def _check(rows: Any) -> Rows:
    """Мінімальна валідація готової колекції."""
    if not isinstance(rows, list) or any(not isinstance(r, Mapping) for r in rows):
        raise ValueError("Expected list of dicts")
    return [dict(r) for r in rows]


@singledispatch
def load_tariffs(src: object) -> Rows:
    """Повертає список словників-тарифів із JSON/CSV-джерела будь-якого типу."""
    raise TypeError(f"Unsupported type: {type(src)!r}")


@load_tariffs.register
def _(src: str) -> Rows:
    """JSON-рядок або шлях до .json/.csv."""
    if src.lstrip().startswith(("[", "{")):
        return _check(json.loads(src))
    return load_tariffs(Path(src))


@load_tariffs.register
def _(src: Path) -> Rows:
    """Файл .json або .csv за розширенням."""
    text = src.read_text(encoding="utf-8")
    if src.suffix.lower() == ".csv":
        return list(csv.DictReader(io.StringIO(text)))
    return _check(json.loads(text))


@load_tariffs.register
def _(src: io.TextIOBase) -> Rows:
    """Відкритий текстовий файл: формат визначається за вмістом."""
    return _parse_text(src.read())


@load_tariffs.register
def _(src: list) -> Rows:  # type: ignore[type-arg]
    """Готова колекція словників."""
    return _check(src)


load_users = load_tariffs
"""Базовий приклад з методички: той самий loader для записів студентів."""

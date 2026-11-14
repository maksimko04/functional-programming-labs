"""Точка входу лабораторної роботи №2, варіант 13."""

import sys

from app import main as run


def main() -> None:
    """Запуск конвеєра розрахунку доставки посилок."""
    run(sys.argv[1:])


if __name__ == "__main__":
    main()

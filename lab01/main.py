"""Точка входу лабораторної роботи №1, варіант 13."""

import sys

from app import main as run


def main() -> None:
    """Запуск програми розрахунку страхових полісів."""
    run(sys.argv)


if __name__ == "__main__":
    main()

"""Варіант 13: паліндроми рекурсивно, з мемоізацією підзадач (left, right).

База рекурсії: рядок довжини 0 або 1 — паліндром. Крок: крайні символи рівні
і внутрішній фрагмент — паліндром. Усі функції чисті, рядки не змінюються.
"""

from __future__ import annotations

from functools import lru_cache


def normalize(s: str) -> str:
    """Лишає лише літери/цифри у нижньому регістрі (casefold для Unicode)."""
    return "".join(ch for ch in s.casefold() if ch.isalnum())


def is_palindrome(s: str) -> bool:
    """Рекурсивна перевірка: база len <= 1, крок — крайні символи + середина."""
    if len(s) <= 1:
        return True
    return s[0] == s[-1] and is_palindrome(s[1:-1])


def is_palindrome_iter(s: str) -> bool:
    """Ітеративна альтернатива з двома індексами — безпечна для довгих рядків."""
    i, j = 0, len(s) - 1
    while i < j:
        if s[i] != s[j]:
            return False
        i, j = i + 1, j - 1
    return True


def _make_is_pal(s: str):  # type: ignore[no-untyped-def]  # ponytail: cache per string
    @lru_cache(maxsize=100_000)
    def is_pal(left: int, right: int) -> bool:
        if left >= right:
            return True
        return s[left] == s[right] and is_pal(left + 1, right - 1)

    return is_pal


def longest_palindrome(s: str) -> str:
    """Найдовший паліндромний фрагмент: рекурсія по межах (left, right) з lru_cache.

    Підзадача is_pal(l, r) кешується, тому кожна пара меж обчислюється один раз
    (O(n²) замість O(n³) для наївного перебору).
    """
    if not s:
        return ""
    is_pal = _make_is_pal(s)
    for length in range(len(s), 0, -1):
        for left in range(0, len(s) - length + 1):
            right = left + length - 1
            if is_pal(left, right):
                return s[left : right + 1]
    return s[0]


@lru_cache(maxsize=100_000)
def longest_len(s: str, left: int, right: int) -> int:
    """Довжина найдовшого паліндромного фрагмента в s[left..right] (з кешем).

    Якщо весь фрагмент паліндром — його довжина; інакше максимум з відкинутим
    лівим або правим символом. Стан (s, left, right) мемоізується.
    """
    if left > right:
        return 0
    if is_palindrome_iter(s[left : right + 1]):
        return right - left + 1
    return max(longest_len(s, left + 1, right), longest_len(s, left, right - 1))


def longest_len_naive(s: str, left: int, right: int) -> int:
    """Та сама рекурсія без кешу — експоненційна, для порівняння часу."""
    if left > right:
        return 0
    if is_palindrome_iter(s[left : right + 1]):
        return right - left + 1
    return max(
        longest_len_naive(s, left + 1, right), longest_len_naive(s, left, right - 1)
    )


def longest_palindrome_iter(s: str) -> str:
    """Ітеративна альтернатива: розширення від центру, O(n²), без рекурсії."""
    best = ""
    for center in range(len(s)):
        for left, right in ((center, center), (center, center + 1)):
            while left >= 0 and right < len(s) and s[left] == s[right]:
                left, right = left - 1, right + 1
            if right - left - 1 > len(best):
                best = s[left + 1 : right]
    return best

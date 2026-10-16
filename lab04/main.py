"""Демо ЛР4: паліндроми, порівняння часу з кешем/без, базові алгоритми."""

from __future__ import annotations

import sys
import timeit

from algorithms import (
    Node,
    bfs_level_order,
    fib,
    fib_iter,
    fib_naive,
    inorder,
    quicksort,
)
from palindromes import (
    is_palindrome,
    longest_len,
    longest_len_naive,
    longest_palindrome,
    longest_palindrome_iter,
    normalize,
)


def main() -> None:
    """Друкує результати та таблицю часу (лише I/O, обчислення чисті)."""
    for s in ["А роза упала на лапу Азора", "Never odd or even", "Привіт"]:
        print(f"{s!r:35} -> {is_palindrome(normalize(s))}")
    text = "abacdfgdcabaxyzzyxq"
    print("longest:", longest_palindrome(text), longest_palindrome_iter(text))

    s = "abcdefghijabcdefghij"
    n = len(s) - 1

    def cached_run() -> int:
        longest_len.cache_clear()
        return longest_len(s, 0, n)

    t_cached = timeit.timeit(cached_run, number=1)
    t_naive = timeit.timeit(lambda: longest_len_naive(s, 0, n), number=1)
    print(f"longest_len({len(s)}) cached: {t_cached * 1e3:.2f} ms")
    print(f"longest_len({len(s)}) naive : {t_naive * 1e3:.2f} ms")
    print("cache_info:", longest_len.cache_info())

    fib.cache_clear()
    print("fib(30) cached:", f"{timeit.timeit(lambda: fib(30), number=1) * 1e3:.3f} ms")
    print(
        "fib(30) naive :",
        f"{timeit.timeit(lambda: fib_naive(30), number=1) * 1e3:.1f} ms",
    )
    print("fib(90) ==", fib(90), "iter:", fib_iter(90))

    print("quicksort:", quicksort([3, 1, 4, 1, 5, 9, 2, 6]))
    t = Node(4, Node(2, Node(1), Node(3)), Node(6, None, Node(7)))
    print("inorder:", list(inorder(t)), "bfs:", bfs_level_order(t))
    print("recursion limit:", sys.getrecursionlimit())


if __name__ == "__main__":
    main()

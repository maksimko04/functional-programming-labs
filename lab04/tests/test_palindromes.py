import timeit

import pytest
from hypothesis import given
from hypothesis import strategies as st
from palindromes import (
    is_palindrome,
    is_palindrome_iter,
    longest_len,
    longest_len_naive,
    longest_palindrome,
    longest_palindrome_iter,
    normalize,
)


@pytest.mark.parametrize(
    ("s", "expected"),
    [
        ("", True),
        ("a", True),
        ("aa", True),
        ("ab", False),
        ("abba", True),
        ("abcba", True),
    ],
)
def test_is_palindrome_edges(s: str, expected: bool) -> None:
    assert is_palindrome(s) is expected
    assert is_palindrome_iter(s) is expected


def test_unicode_and_normalize() -> None:
    assert is_palindrome(normalize("А роза упала на лапу Азора"))
    assert is_palindrome(normalize("Я — ґаздиня, я!")) is False
    assert is_palindrome("шалаш") and is_palindrome("ñañ") and is_palindrome("ΑΒΑ")
    assert normalize("Ab, c!") == "abc"


def test_longest_palindrome_known() -> None:
    assert longest_palindrome("babad") in {"bab", "aba"}
    assert longest_palindrome("cbbd") == "bb"
    assert longest_palindrome("abacdfgdcabaxyzzyxq") == "xyzzyx"
    assert longest_palindrome("") == ""
    assert longest_palindrome("x") == "x"
    assert longest_palindrome("абвба") == "абвба"


def test_longest_len_cache_api() -> None:
    longest_len.cache_clear()
    s = "abcbaxyz"
    assert longest_len(s, 0, len(s) - 1) == 5
    info = longest_len.cache_info()
    assert info.misses > 0
    longest_len(s, 0, len(s) - 1)
    assert longest_len.cache_info().hits == info.hits + 1
    longest_len.cache_clear()
    assert longest_len.cache_info().currsize == 0


def test_cached_matches_naive_and_faster() -> None:
    s = "abcdefghijabcdefgh"
    n = len(s) - 1
    longest_len.cache_clear()
    assert longest_len(s, 0, n) == longest_len_naive(s, 0, n) == 1
    t_naive = timeit.timeit(lambda: longest_len_naive(s, 0, n), number=1)

    def cached_run() -> int:
        longest_len.cache_clear()
        return longest_len(s, 0, n)

    t_cached = timeit.timeit(cached_run, number=1)
    assert t_cached < t_naive


def test_input_not_mutated() -> None:
    s = "racecar"
    longest_palindrome(s)
    is_palindrome(s)
    assert s == "racecar"


@given(st.text(max_size=40))
def test_property_recursive_equals_iterative(s: str) -> None:
    assert is_palindrome(s) == is_palindrome_iter(s)
    assert len(longest_palindrome(s)) == len(longest_palindrome_iter(s))
    assert len(longest_palindrome(s)) == longest_len(s, 0, len(s) - 1) if s else True


@given(st.text(max_size=20))
def test_property_doubled_string_is_palindrome(s: str) -> None:
    assert is_palindrome(s + s[::-1])
    assert len(longest_palindrome(s + s[::-1])) >= 2 * len(s)

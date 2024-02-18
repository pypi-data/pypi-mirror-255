"""Define utility methods for working with strings.
"""
from __future__ import annotations

import logging
import re

logger = logging.getLogger(__name__)


def get_all_numbers(s: str) -> list[str]:
    """Return a list of all substrings (left-to-right) in s that contain only digits."""
    return re.findall(r"\d+", s)


def get_alphanum_split(s: str) -> tuple[str, str]:
    """Return a tuple of two lists, one consisting of the digits in s (as strings) and the other
    the letters in s, maintaining the left-to-right order in each."""
    return get_digits(s), get_letters(s)


def get_digits_as_list(s: str) -> list[str]:
    """Return the characters from string s that are digits, as list of strings."""
    z = [i for i in get_digits(s)]
    return z


def get_digits(s: str) -> str:
    """Return the characters from string s that are digits, as a string."""
    return "".join([c for c in s if c.isdigit()])


def get_letters(s: str) -> str:
    """Return the characters from string s that are letters, as a string."""
    return "".join([c for c in s if c.isalpha()])


def get_ordinal(n: int) -> str:
    """Return the ordinal of the given number as a string."""
    suffixes = {1: "st", 2: "nd", 3: "rd"}
    if 10 <= n % 100 <= 20:
        suffix = "th"
    else:
        suffix = suffixes.get(n % 10, "th")
    return str(n) + suffix


def is_left_substring(str1: str, str2: str) -> bool:
    """Return True if str2 is (1) at least three characters in length and (2) is a substring of
    str1, starting from the left-most character and ignoring case. Not commutative."""
    return len(str2) >= 3 and str1.lower().startswith(str2.lower())


def multi_replace(s: str, *, rmap: dict) -> str:
    """Return a new string in which the replacements specified by the given dictionary (rmap) have
    been applied sequentially starting with source string (s).
    """
    for k, v in rmap.items():
        s = s.replace(k, v)
    return s


def remove_text_inside_brackets(text: str, brackets: str = "()[]") -> str:
    """https://stackoverflow.com/questions/14596884/remove-text-between-and"""
    count = [0] * (len(brackets) // 2)  # count open/close brackets
    saved_chars = list()
    queued_chars = list()  # an intermediate list

    for character in text:
        for i, b in enumerate(brackets):
            if character == b:  # found bracket
                kind, is_closed = divmod(i, 2)
                count[kind] += (-1) ** is_closed  # `+1`: open, `-1`: close

                # If this bracket is never closed, we want to keep it.

                if count[kind] == 1:  # open bracket
                    queued_chars.append(character)

                if count[kind] < 0:  # unbalanced bracket
                    count[kind] = 0  # keep it
                else:  # found bracket to remove
                    queued_chars = []
                    break
        else:  # character is not a [balanced] bracket
            if not any(count):  # outside brackets
                saved_chars.append(character)
            else:
                queued_chars.append(character)

    saved_chars += queued_chars

    return str().join(saved_chars).strip()

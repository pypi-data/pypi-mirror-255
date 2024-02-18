import re
from typing import Iterator


def notation_to_integer_generator(notation: str, raise_errors: bool = False) -> Iterator[int]:
    """Converts a notation string into an iterator of integers.

    Permitted formats:
    - Single values: '10', '-20', '0'
    - Ranges: '10-30', '-20--10'
    - Ranges with step: '10-30/5', '-20--10/2'
    - Mixed formats separated by commas: '10-30,42,55,0--10/2,90-96'

    Args:
        notation (str): The notation string to parse.
        raise_errors (bool, optional): If True, raises ValueError for invalid tokens.
            Defaults to False.

    Yields:
        Iterator[int]: An iterator of integers parsed from the notation string.
    """
    rule_simple = re.compile(r"(?P<value>\-?\d+)$")
    rule_with_range = re.compile(r"(?P<start>\-?\d+)-(?P<end>\-?\d+)$")
    rule_with_range_and_step = re.compile(r"(?P<start>\-?\d+)-(?P<end>\-?\d+)/(?P<step>\-?\d+)$")

    for token in notation.split(","):
        token = token.strip()
        if match := rule_simple.match(token):
            yield int(match.group("value"))
        elif match := rule_with_range.match(token):
            start, end = map(int, match.groups())
            step = 1 if start < end else -1
            yield from range(start, end + step, step)
        elif match := rule_with_range_and_step.match(token):
            start, end, step = map(int, match.groups())
            direction = -1 if end < start else 1
            step = abs(step) if direction == 1 else -abs(step)
            yield from range(start, end + direction, step)
        elif raise_errors:
            raise ValueError(f"Invalid token {token}")


import sys

if __name__ == "__main__":
    print(list(notation_to_integer_generator(sys.argv[1], True)))

from typing import Iterable


def flatten(xs: Iterable) -> list:
    """
    Converts an arbitrarily deeply nested list
      [[1, 2], [3, 4, 5], [6, [7, [8, 9]]]]
    into a single flattened list
      [1, 2, 3, 4, 5, 6, 7, 8, 9]
    """
    result = []
    for x in xs:
        if isinstance(x, list):
            result.extend(flatten(x))
        else:
            result.append(x)
    return result

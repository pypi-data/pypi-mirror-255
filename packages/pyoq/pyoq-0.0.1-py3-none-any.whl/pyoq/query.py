from enum import Enum
from typing import Any, Iterable, Tuple, Union

"""
Grammar:

E  -> T[.E]*
T  -> K|[I]|I:I
K  -> Python valid identifiers.
      see: https://docs.python.org/3/reference/lexical_analysis.html#identifiers
I  -> [-][0-9]+
"""


class Operation(Enum):
    ATTR = "Attribute"
    KEY = "Key"
    INDEX = "Index"
    RANGE = "Range"


def parse_query(
    query: str,
) -> Iterable[Tuple[Operation, Union[str, int, Tuple[int, int]]]]:

    def parse_attr(subquery: str) -> str:
        if not subquery.isidentifier():
            raise ValueError(f"Invalid key: {subquery}")
        return subquery

    def parse_index(subquery: str) -> int:
        return int(subquery)

    if not query:
        raise ValueError(f"Blank query")

    for subquery in query.split("."):
        if "[" == subquery[0]:
            yield Operation.INDEX, parse_index(subquery[1:-1])
            continue

        if ":" in subquery:
            start, end = subquery.split(":")
            yield Operation.RANGE, (parse_index(start), parse_index(end))

        try:
            yield Operation.ATTR, parse_attr(subquery)
            continue

        except ValueError:
            yield Operation.KEY, subquery
            continue


def query(obj: Any, query: str, default: Any = None) -> Any:
    """
    Use JQ style 'something.by.dot' syntax to retrieve objects from Python
    objects.

    Usage:
       >>> x = {"top": {"middle" : {"nested": "value"}}}
       >>> query(x, "top.middle.nested")
       "value"
    """

    val = obj
    for operation, key in parse_query(query):
        if operation == Operation.ATTR:
            try:
                val = getattr(val, key)
            except AttributeError:
                try:
                    val = val[key]
                except (KeyError, TypeError):
                    return default

        elif operation == Operation.KEY:
            try:
                val = val[key]
            except (KeyError, TypeError):
                return default

        elif operation == Operation.INDEX:
            try:
                val = val[key]
            except IndexError:
                return default

        elif operation == Operation.RANGE:
            start, end = key
            return val[start:end]

    return val

"""
Utility functions for parsing and converting string formats.
"""

import re


def to_camel_case(snake_str: str) -> str:
    """
    Convert a snake_case string to camelCase.

    Args:
        snake_str (str): The snake_case string to convert.
    Returns:
        str: The converted camelCase string.
    """
    components = snake_str.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


def to_snake_case(camel_str: str) -> str:
    """
    Convert a camelCase string to snake_case.

    Args:
        camel_str (str): The camelCase string to convert.
    Returns:
        str: The converted snake_case string.
    """
    return re.sub(r"(?<!^)(?=[A-Z])", "_", camel_str).lower()

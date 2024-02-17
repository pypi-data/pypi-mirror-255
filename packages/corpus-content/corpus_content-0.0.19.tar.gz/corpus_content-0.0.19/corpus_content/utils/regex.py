import re

FOOTNOTE_IN_HEADING = r"\[\^\d+\]"
PARENTHESIS_ACRONYM = r"\([A-Z]{2,4}\)"


def add_terminal_options(raw: str):
    return rf"{raw}(\s*{PARENTHESIS_ACRONYM})?(\s*{FOOTNOTE_IN_HEADING})?"


def jx(regexes: list[str], border: str = r"\s+", enclose: bool = False) -> str:
    """Joins regex strings (i.e. `regexes`) using a `border`.

    Args:
        regexes (list[str]): Raw regex strings to be joined
        border (str, optional): A regex string to be set in between `regexes`. Defaults to \r"\\s+".
        enclose (bool, optional): Whether each regex string joined should have a wrapping parenthesis `(<regex-string>)`. Defaults to False.

    Returns:
        str: A raw regex string for pattern matching.
    """  # noqa: E501

    if enclose:
        regexes = [rf"({reg})" for reg in regexes]
    return border.join(regexes)

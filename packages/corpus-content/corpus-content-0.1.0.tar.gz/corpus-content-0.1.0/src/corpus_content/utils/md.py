import re
from io import StringIO

from markdown import Markdown  # type: ignore

footnote_pattern = re.compile(r"\[\^\d+\]")

two_or_more_spaces = re.compile(r"\s{2,}")


def unmark_element(element, stream=None):
    if stream is None:
        stream = StringIO()
    if element.text:
        stream.write(element.text)
    for sub in element:
        unmark_element(sub, stream)
    if element.tail:
        stream.write(element.tail)
    return stream.getvalue()


# patching Markdown
Markdown.output_formats["plain"] = unmark_element  # type: ignore
__md = Markdown(output_format="plain")  # type: ignore
__md.stripTopLevelTags = False  # type: ignore


def clear_markdown(value: str) -> str:
    """Given markdown text, strip markdown elements to get the raw text.

    1. Uses part of the code described in https://stackoverflow.com/a/54923798/9081369
    2. Will remove footnotes
    """  # noqa: E501
    unmarked = __md.convert(value)
    result = footnote_pattern.sub("", unmarked)
    result = two_or_more_spaces.sub(" ", result)
    return result

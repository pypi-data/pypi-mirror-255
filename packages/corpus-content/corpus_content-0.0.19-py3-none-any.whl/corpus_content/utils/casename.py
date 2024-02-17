import re

italicized_case = re.compile(
    r"""
    \*{3} # marker
    (?P<casename>
        (.+?)
        (\svs?\.\s)
        (.+?)
    )
    \*{3} # marker
    """,
    re.X,
)


def clean_vs_casename(text: str):
    while True:
        if match := italicized_case.search(text):
            text = text.replace(match.group(), f"*{match.group('casename')}*")
        else:
            break
    return text

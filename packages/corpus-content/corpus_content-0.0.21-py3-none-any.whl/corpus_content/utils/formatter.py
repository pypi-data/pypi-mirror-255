import re
from pathlib import Path

import frontmatter  # type: ignore

from .annex import clean_annex
from .casename import clean_vs_casename
from .dumper import SafeDumper
from .fallo import add_fallo_comment
from .phrase import Phrase

phrases = Phrase.generate_regex_unnamed()


def clean_headings(text: str):
    for phrase in re.finditer(rf"\*+(?P<heading>{phrases}):?\*+\s+", text):
        matched_text = phrase.group()
        if heading := phrase.group("heading"):
            text = text.replace(matched_text, f"\n## {heading}\n\n")
    return text


candidate = re.compile(
    r"""^\*+ # starts with open asterisk
    \s* # optional space
    (?P<candidate>
        [\w\s:,'\-\–\.\(\)\*;\/\"&%\^’]{15,65} # first line, must contain at least 15 characters
        (
            \n # can be an empty line
            ([\w\s:,'\-\–\.\(\)\*;\/\"&%\^’]{5,65})? # non-empty line may contain shorter string (5)
        )+ # subsequent lines
        \?? # may end with a question mark
    )
    \*+ # ends with closing asterisk
    (\.?)? # ending punctuation can follow asterisk
    (\[\^\d+\])? # footnote can follow asterisk
    \n{2} # terminates in two new lines
    """,  # noqa: E501
    re.M | re.X,
)


def clean_candidates(text: str):
    for phrase in candidate.finditer(text):
        matched_text = phrase.group()
        if heading := phrase.group("candidate"):
            revised = re.sub(r"\n+", " ", heading).strip("* ")
            text = text.replace(matched_text, f"\n### {revised}\n\n")
    return text


def formatter(text: str, is_main: bool = False):
    text = clean_headings(text)
    text = clean_candidates(text)
    text = clean_vs_casename(text)
    if is_main:
        text = add_fallo_comment(text)
    text = clean_annex(text)
    return text


possibles = re.compile(
    r"""
    \n
    ^\*+
    (?P<possible>.+)
    \*+$\n
    """,
    re.X | re.M,
)

all_caps = re.compile(
    r"""
    \n
    ^\s*
    (?P<capped>[A-Z]{3,}[A-Z0-9\s\.]+)
    $
    """,
    re.X | re.M,
)


def is_ok_endnote_format(text: str) -> str | None:
    for i in [1, 2]:
        base = rf"\[\^{i}\]"
        if len(re.findall(rf"{base}", text)) == 2:
            if re.search(rf"^{base}:", text, flags=re.M):
                return str(i)
    return None


def detect_possible_headings(text: str) -> list[str]:
    texts = []
    for matched in possibles.finditer(text):
        text = matched.group("possible").strip("* ")
        evaluated = text.lower()
        if "so ordered" in evaluated:
            continue
        if evaluated.startswith("wherefore"):
            continue
        texts.append(text)

    for cap in all_caps.finditer(text):
        text = cap.group("capped")
        evaluated = text.lower()
        if "so ordered" in evaluated:
            continue
        texts.append(text)

    return texts


def update_content(file: Path) -> list[str]:
    is_main = "main" in file.stem
    meta = frontmatter.load(file)  # type: ignore
    text = formatter(text=meta.content, is_main=is_main)
    post = frontmatter.Post(text, **meta.metadata)  # type: ignore
    frontmatter.dump(post=post, fd=file, Dumper=SafeDumper)  # type: ignore
    headings = detect_possible_headings(post.content)
    return headings

import re
from collections.abc import Iterator
from typing import NamedTuple, Self

NOTE_INDICATOR = re.compile(r"\n(?=\[\^[\w-]+\]:)", re.M)


sp_at_start = re.compile(r"^\s+(?=.*)", re.M)
"""New line starting with at least one space."""

footnote_sentence_pattern = re.compile(
    r"""
    \. # a period signifies a sentence
    \[ # start of marker
    \^ # marker of a footnote
    \d{1,3}-?\w? # footnote reference
    \] # end of marker
    """,
    re.X,
)


class Footnote(NamedTuple):
    reference: str
    value: str

    @property
    def pointer(self):
        """A raw regex string based on the reference of the footnote.
        This is used to help create proper indentions for multi-line footnotes
        in the markdown file.
        """
        return f"[^{self.reference}]: "

    @property
    def as_markdown(self):
        """Each footnote's multiline value (after the first line)
        should begin with an additional four spaces for proper
        indention.
        """
        texts = self.value.split("\n")
        for idx, line in enumerate(texts):
            if line and idx != 0:  # line = not blank, != after first line
                texts[idx] = f"    {line}"  # 4 spaces = tab
        return self.pointer + "\n".join(texts)

    @classmethod
    def from_marker(cls, text: str):
        """Does the text start with a marker? If yes, extract
        the parts of a footnote so that multi-line processing
        can be done."""
        if match := re.search(r"(^\[\^(?P<marker>[\w-]+)\]:)", text):
            return cls(
                reference=match.group("marker"),
                value=text.removeprefix(match.group()).strip(),
            )

    @classmethod
    def gather(cls, text: str) -> Iterator[Self]:
        """Given annex text, generate a list of Footnote instances"""
        start_text = sp_at_start.sub("\n\n", text)
        notes = NOTE_INDICATOR.split(start_text)
        for note in notes:
            if matched := cls.from_marker(text=note):
                yield matched

    @classmethod
    def slice_by(cls, chunk: str) -> Iterator[str]:
        """Creates passages by slicing with the footnote sentence pattern, if it exists;
        if no more patterns are found within the chunk, then the remainder.

        Args:
            chunk (str): Ideally, the body's Chunk.text to use for further splitting.

        Yields:
            Iterator[str]: Sub-chunks based on the `footnote_sentence_pattern`
        """
        while True:
            if match := footnote_sentence_pattern.search(chunk):
                if partial := chunk[: match.end()].strip():
                    yield partial
                chunk = chunk[match.end() :]
            else:
                if partial := chunk.strip():
                    yield partial
                break


class Annex(NamedTuple):
    footnotes: list[Footnote]

    @classmethod
    def detect_initial_footnote(cls, text: str, start: int = 1) -> int | None:
        """Uses a conventional footnote pattern, the important part
        being the terminal character `:`. This signifies that the pattern
        represents an item found in the Annex rather than in the body of the `text`.

        Args:
            text (str): The body to cut off
            start (int, optional): Footnote number to start. Defaults to 1.

        Returns:
            int | None: Cutoff point based on a footnote number
        """
        try:
            return text.index(f"[^{start}]:")
        except ValueError:
            return None

    @classmethod
    def lookup_index(cls, text: str) -> int | None:
        """Some annexes may not contain properly formatted footnote references; in this case, the raw opinion text (body + annex) must be split on the earliest footnote (max value: 5); if found then the text can be split at the index generated to get the annex proper.

        Args:
            text (str): The body to cut off

        Returns:
            int | None: Cutoff point based on a footnote number
        """  # noqa: E501
        for ref in range(1, 5):
            if detected := Annex.detect_initial_footnote(text, start=ref):
                return detected
        return None

    @property
    def as_markdown(self):
        return "\n\n".join([f.as_markdown for f in self.footnotes])


def clean_annex(text: str):
    index = Annex.lookup_index(text)
    if not index:
        return text

    body = text[:index]
    raw_annex = text[index:].removesuffix("---")
    formatted_annex = Annex(footnotes=list(Footnote.gather(raw_annex))).as_markdown
    return body + formatted_annex + "\n"

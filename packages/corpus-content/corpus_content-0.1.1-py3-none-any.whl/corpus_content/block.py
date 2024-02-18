import re
from collections import abc, deque
from typing import NamedTuple, Self

from .utils import Footnote

fn_pattern = re.compile(
    r"""
        \[ # start of marker
        \^ # marker of a footnote
        (?P<fv>[\w-]+) # assumes already a proper value
        \] # end of marker
    """,
    re.X,
)


class Passage(NamedTuple):
    material_path: str
    text: str
    footnotes: list[str]


class Chunk(NamedTuple):
    order: int
    material_path: str
    text: str
    category: str | None = None

    def __repr__(self) -> str:
        return f"<Chunk {self.material_path}>: {len(self.text)} - {self.category or 'uncategorized'}: {self.text[:30]}.."  # noqa: E501

    @property
    def passages(self):
        num = len(fn_pattern.findall(self.text))
        if num >= 2:
            for cnt, item in enumerate(Footnote.slice_by(self.text)):
                yield Passage(
                    material_path=f"{self.material_path}{cnt}.",
                    text=item,
                    footnotes=[m.group("fv") for m in fn_pattern.finditer(item)],
                )
        else:
            yield Passage(
                material_path=f"{self.material_path}0.",
                text=self.text,
                footnotes=[m.group("fv") for m in fn_pattern.finditer(self.text)],
            )

    @property
    def as_row(self):
        from .utils import clear_markdown

        text = clear_markdown(self.text).strip()
        data = self._asdict()
        data["text"] = text
        data["char_count"] = len(self.text)
        return data


class Block(NamedTuple):
    """Each opinion, especially the main opinion, can be subdivided into blocks of text.

    A `body` of text passed can be broken down further into `@children` blocks. The division is
    based on semi-automated markdown headers.

    The rationale for is to create better text segmentation of an opinion.

    This assumes that the `body` of text contains a `heading_level` starting with 2,
    e.g. 2 `#` characters, but may contain nested blocks within:

    ```markdown
    ## Sample heading 1

    A paragraph

    ### Another heading underneath 1

    ## Sample heading 2

    > hello world
    ```

    The `material_path` starts with "1." and all child blocks will inherit
    from this as the root path.

    The heading `title` may be:

    1. a `marker` which divides text such as roman numeral, a letter, a number, e.g. `I.`, `I.A.4`, etc.; or
    2. a `label`, akin to a chapter in a book, e.g. `Ruling of the Court`, `Issues`, `Antecedent Facts`, etc. or
    3. a `phrase`, akin to a section inside a chapter, e.g. `There is not enough evidence to... xxx`

    """  # noqa: E501

    material_path: str = "1."
    heading_level: int = 2
    inherited_category: str | None = None
    title: str | None = None
    body: str = ""
    order: int | None = None

    def __repr__(self) -> str:
        if self.title:
            return f"<Block {self.inherited_category or 'x'}-{self.material_path}: {self.title}>"  # noqa: E501
        return f"<Block {self.inherited_category or 'x'}-{self.material_path}>"

    @property
    def proper_body(self):
        """The text may contain hidden comments which are formatted in header form;
        remove these from the body before dividing into component parts."""
        if self.body.strip():
            raw = self.body
            for match in re.finditer(r"<!--\s*(?P<heading>.*)\s*-->", raw):
                raw = raw.replace(match.group(), match.group("heading"))
            return raw
        return self.body

    @property
    def heading_regex(self):
        """Uses explicit number of `#` characters for regex pattern creation."""
        return rf"^#{ {self.heading_level} }\s"

    @property
    def divider(self) -> re.Pattern:
        """Pattern to split `body` into `@children`; uses `\\n` prior to the `@heading_regex`."""  # noqa: E501
        return re.compile(rf"\n(?={self.heading_regex})", re.M)

    def get_heading_text(self, text: str) -> str | None:
        """Uses pattern to extract `title` of each block yield from `@children`."""
        if match := re.search(rf"(?<={self.heading_regex}).*", text):
            return match.group().strip()
        return None

    def get_body_text(self, text: str) -> str:
        """Uses pattern to extract `body` of each block yield from `@children`."""
        return re.sub(rf"{self.heading_regex}.*", "", text).strip()

    def get_children(self):
        """Each `body` may be split into component sub-blocks.

        The splitter should result in at least two parts; if the body isn't split
        then no children blocks result.
        """
        from .utils import categorize_header

        children = list(self.divider.split(self.proper_body))
        if len(children) == 1:
            return None

        head_cat = categorize_header(self.title) if self.title else None
        for counter, subcontent in enumerate(children, start=1):
            subtitle = None
            subcat = None
            if subtitle := self.get_heading_text(subcontent):
                subcat = categorize_header(subtitle)
            yield Block(
                material_path=self.material_path + f"{counter}.",
                heading_level=self.heading_level + 1,
                inherited_category=subcat or head_cat or self.inherited_category,
                title=subtitle,
                body=self.get_body_text(subcontent),
            )

    def get_blocks(self) -> abc.Iterator[Self]:
        """Recursive function to get all blocks, with each
        block getting its own nested children."""
        yield self

        children = list(self.get_children())
        if not children:
            return
        q = deque(children)

        while True:
            try:
                blk = q.popleft()
            except IndexError:
                break
            yield from blk.get_blocks()

    @property
    def blocks(self):
        """Each block can be divided into child blocks, i.e.
        divisions based on markdown headers."""
        blks = list(self.get_blocks())
        if len(blks) != 1:
            for cnt, blk in enumerate(blks[1:]):
                data = blk._asdict()
                data["order"] = cnt
                yield Block(**data)

    @property
    def chunks(self) -> list[Chunk]:
        """Each block can be divided into semantic chunks; a chunk
        consists of blockquotes which often pollute opinions (once converted from html).
        So one quick way of splitting a block's body into chunks is to split on lines
        that do not start with a blockquote, e.g.

        ```markdown
        A. This is the start of a block

        B. This is the middle of a block

        > B.1 This is a blockquote

        C. This is the end of a block
        ```

        The entire block above will be split on: A, B, and C.
        """  # noqa: E501
        results = []
        bits = re.split(r"\n\n(?!>)", self.proper_body)
        for counter, bit in enumerate(bits, start=1):
            if v := bit.strip():
                cat = self.inherited_category
                mp = f"{self.material_path}{counter}."
                chunk = Chunk(order=counter, category=cat, material_path=mp, text=v)

                # Do not include headings since these can be
                # retrieved separately via get_headings()
                if chunk.text.startswith("#"):
                    continue
                results.append(chunk)
        return results

    @classmethod
    def get_headings(cls, text: str) -> abc.Iterator[Self]:
        for blk in cls(body=text).blocks:
            if blk.title:
                yield blk

import logging
from collections.abc import Iterator
from dataclasses import asdict, dataclass, field
from enum import StrEnum, auto
from functools import cached_property

from citation_utils import CountedCitation  # type: ignore
from statute_utils import CountedStatute  # type: ignore

from .block import Block, fn_pattern
from .utils import Annex, Footnote


class ArtifactCategory(StrEnum):
    citation = auto()
    vs = auto()
    ref = auto()
    docket = auto()
    unit = auto()
    rule = auto()
    statute = auto()


@dataclass
class Artifact:
    text: str
    category: ArtifactCategory
    count: int

    @property
    def as_row(self):
        data = asdict(self)
        data.pop("category")
        data["category"] = self.category.name
        return data

    @classmethod
    def from_phrases(cls, phrases: list[str]):
        artifacts = []
        for phrase in phrases:  # type: ignore
            if objs := phrase.split("__"):
                if len(objs) == 3:
                    artifacts.append(
                        Artifact(
                            text=objs[0],
                            category=ArtifactCategory[objs[1]],
                            count=int(objs[2]),
                        )
                    )
        return artifacts


@dataclass
class Segment:
    id: str
    order: int
    decision_id: str
    opinion_id: str
    material_path: str
    text: str
    footnotes: list[dict] = field(default_factory=list)
    category: str | None = None

    def __repr__(self) -> str:
        return f"<Segment {self.material_path}: fn {len(self.footnotes)}>"  # noqa: E501

    @cached_property
    def as_row(self):
        from .utils import clear_markdown

        data = asdict(self)
        data.pop("footnotes")
        data["text"] = clear_markdown(fn_pattern.sub("", self.text))
        data["char_count"] = len(data["text"])
        return data


@dataclass
class Opinion:
    """Whether the opinion is the main opinion of the decision
    or a separate one, it will contain common fields and associated
    records based on the content.
    """

    id: str
    decision_id: str
    content: str
    justice_id: int | None = None
    is_main: bool = True
    label: str = "Opinion"
    file_statutes: str | None = None
    file_citations: str | None = None
    file_artifacts: list[Artifact] | None = None

    def __repr__(self) -> str:
        return f"<Opinion {self.id}>"

    @cached_property
    def row(self):
        return {"opinion_id": self.id, "decision_id": self.decision_id}

    @cached_property
    def index(self):
        return Annex.lookup_index(self.content)

    @cached_property
    def body(self) -> str:
        """The text representing the body proper."""
        return self.content[: self.index] if self.index else self.content

    @cached_property
    def annex(self) -> str | None:
        """The text representing the annex proper."""
        return self.content[self.index :] if self.index else None

    @cached_property
    def footnotes_list(self) -> list[Footnote]:
        """Itemizes the list of Footnote objects found in the @annex"""
        return list(Footnote.gather(self.annex)) if self.annex else []

    @cached_property
    def blocks(self) -> list[Block]:
        """Hierarchical content:

        - `Opinion` - may consist of a _body_ and an Annex
            - `Block` - a _body_ division based on a _natural_ or _artificial_ header
        """
        return list(Block(body=self.body).blocks)

    def get_segments(
        self,
        with_footnotes_only: bool = False,
        only_ruling_chunks: bool = False,
    ) -> Iterator[Segment]:
        """Hierarchical content:

        - `Opinion` - may consist of a body and an Annex
            - `Block` - a body division based on a _natural_ or _artificial_ header
                - `Chunk` - a formula-based division of a block (e.g. include blockquotes)
                    - `Passage` - a chunk divided into "sentences which end in footnotes"

        Construction of a `Segment`
        - The `Annex` contains a list of `Footnote`s.
        - Each `Passage` will contain a footnote reference.
        - A segment consists of a passage and a list of sliced footnotes relevant to the passage.
        - This makes it possible to match passages with their referenced footnotes.

        Args:
            with_footnotes_only (bool, optional): If True, will only gather passages with footnotes detected. Defaults to False.
            only_ruling_chunks (bool, optional): If True, will only gather passages part of the ruling block. Defaults to False.

        Yields:
            Iterator[Segment]: Gathered segments found in the body, matched with their footnotes.
        """  # noqa: E501
        counter = 1
        seen = []
        for block in self.blocks:
            for chunk in block.chunks:
                if only_ruling_chunks and chunk.category != "ruling":
                    continue

                for passage in chunk.passages:
                    if with_footnotes_only and not passage.footnotes:
                        continue
                    if passage.text in seen:
                        continue

                    segment_id = f"{self.id}-{passage.material_path}"

                    footnotes = []
                    for subnote in passage.footnotes:
                        try:
                            footnotes.append(
                                {
                                    "id": f"{segment_id}{subnote}.",
                                    "segment_id": segment_id,
                                    "reference": subnote,
                                }
                            )
                        except Exception as e:
                            logging.error(f"Bad {subnote=}; see {segment_id}; {e}")

                    segment = Segment(
                        id=segment_id,
                        decision_id=self.decision_id,
                        opinion_id=self.id,
                        material_path=passage.material_path,
                        text=passage.text,
                        category=chunk.category,
                        footnotes=footnotes,
                        order=counter,
                    )
                    if segment.as_row["char_count"]:
                        seen.append(passage.text)
                        yield segment
                        counter += 1

    @cached_property
    def footnotes(self) -> list[dict]:
        """Will be used as part of a decision's collection."""
        return [
            {"id": f"{self.id}-{fn.reference}"} | self.row | fn._asdict()
            for fn in self.footnotes_list
        ]

    @cached_property
    def interim_segments(self) -> list[Segment]:
        return list(self.get_segments())

    @cached_property
    def segment_footnotes(self) -> list[dict]:
        return [
            segment_note | {"footnote_id": fn["id"]}
            for segment in self.interim_segments
            for segment_note in segment.footnotes
            for fn in self.footnotes
            if fn["reference"] == segment_note["reference"]
        ]

    @cached_property
    def segments(self) -> list[dict]:
        return [seg.as_row for seg in self.interim_segments]

    @cached_property
    def headings(self) -> list[dict]:
        """Will be used as part of a decision's collection."""
        res = []
        for blk in self.blocks:
            if blk.title:
                data = {}
                data["id"] = f"{self.id}-{blk.material_path}"
                data |= blk._asdict()
                data |= self.row
                data["category"] = data.pop("inherited_category")
                data.pop("body")
                res.append(data)
        return res

    @cached_property
    def statutes(self) -> list[dict]:
        """Will be used as part of a decision's collection."""
        res = []
        if self.file_statutes:
            objs = CountedStatute.from_repr_format(self.file_statutes.split("; "))
            for obj in objs:
                data = {"cat": obj.cat, "num": obj.num, "mentions": obj.mentions}
                data |= self.row
                res.append(data)
        return res

    @cached_property
    def citations(self) -> list[dict]:
        """Will be used as part of a decision's collection."""
        res = []
        if self.file_citations:
            objs = CountedCitation.from_repr_format(self.file_citations.split("; "))
            for obj in objs:
                data = obj.model_dump()
                data |= self.row
                res.append(data)
        return res

    @cached_property
    def artifacts(self) -> list[dict]:
        """Will be used as part of a decision's collection."""
        res = []
        if self.file_artifacts:
            for artifact in self.file_artifacts:
                data = artifact.as_row
                data |= self.row
                res.append(data)
        return res

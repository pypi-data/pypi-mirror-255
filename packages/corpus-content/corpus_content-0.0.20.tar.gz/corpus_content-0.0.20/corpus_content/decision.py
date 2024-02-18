import re
from dataclasses import asdict, dataclass
from functools import cached_property
from pathlib import Path
from typing import Any, NamedTuple

import frontmatter  # type: ignore
from citation_utils import Citation  # type: ignore

from .author import get_writer_from_path
from .opinion import Artifact, Opinion


class Line(NamedTuple):
    text: str
    meta: dict

    @classmethod
    def prep(cls, segments, include_regex: str | None = None):
        for segment in segments:
            v = str(segment["text"]).strip()
            checker = v.lower()
            if len(v) <= 10:
                continue
            if include_regex:
                if not re.search(include_regex, segment["text"]):
                    continue
            if v == "SO ORDERED.":
                continue
            elif v.startswith("^*^ "):
                continue
            elif v.startswith("^**^ "):
                continue
            elif v.startswith("^***^ "):
                continue
            elif v.startswith("^^"):
                continue
            elif v.startswith("(") and v.endswith(")"):
                if "citation" in checker and "omitted" in checker:
                    continue
                for mark in ("emphasis", "italics", "underscoring"):
                    for predicate in ("supplied", "in the original"):
                        if mark in checker and predicate in checker:
                            continue

            data: dict[str, Any] = {}
            data["meta"] = {}
            for key, v in segment.items():
                if key == "text":
                    data["text"] = v
                elif key == "id":
                    data["meta"]["source"] = v
                elif key == "category" and v:
                    data["meta"]["part"] = v
            yield cls(**data)

    @classmethod
    def fn(cls, footnotes, include_regex: str | None = None):
        for footnote in footnotes:
            v = str(footnote["value"]).strip()
            checker = v.lower()
            if len(v) <= 10:
                continue
            if include_regex:
                if not re.search(include_regex, footnote["value"]):
                    continue
            if v == "SO ORDERED.":
                continue
            elif v.startswith("^*^ "):
                continue
            elif v.startswith("^**^ "):
                continue
            elif v.startswith("^***^ "):
                continue
            elif v.startswith("^^"):
                continue
            elif v.startswith("(") and v.endswith(")"):
                if "citation" in checker and "omitted" in checker:
                    continue
                for mark in ("emphasis", "italics", "underscoring"):
                    for predicate in ("supplied", "in the original"):
                        if mark in checker and predicate in checker:
                            continue

            data: dict[str, Any] = {}
            data["meta"] = {}
            for key, v in footnote.items():
                if key == "value":
                    data["text"] = v.replace("*", "").strip()
                elif key == "id":
                    data["meta"]["source"] = v
            yield cls(**data)


class Vote(NamedTuple):
    id: str
    opinion_id: str
    decision_id: str
    text: str
    char_count: int


class Collection(NamedTuple):
    opinions: list[dict]
    statutes: list[dict]
    citations: list[dict]
    headings: list[dict]
    segments: list[dict]
    footnotes: list[dict]
    segment_footnotes: list[dict]
    artifacts: list[dict]


@dataclass
class Decision:
    id: str
    citation: Citation
    title: str
    main_opinion: Opinion
    separate_opinions: list[Opinion]
    votes: list[Vote]
    short: str | None = None
    justice_id: int | None = None
    curiam: bool = False
    category: str | None = None
    composition: str | None = None

    def __repr__(self) -> str:
        return f"<Decision {self.id}>"

    @cached_property
    def vote_rows(self):
        """Database-insertable row made for the _votes_ table."""
        return [v._asdict() for v in self.votes]

    @cached_property
    def citation_row(self):
        """Database-insertable row made for the _citations_ table."""
        data = self.citation.make_docket_row()
        if not data:
            raise Exception("Could not generate citation data")
        data.pop("id")
        return data

    @cached_property
    def case_row(self):
        """Database-insertable row made for the _decisions_ table."""
        return {
            "id": self.id,
            "category": self.category,
            "composition": self.composition,
            "title": self.title,
            "short": self.short,
            "justice_id": self.justice_id,
            "curiam": self.curiam,
        }

    @cached_property
    def related(self):
        """Related database-insertable rows based on a decision file path."""
        opinion_rows = []
        included_statutes = []
        included_citations = []
        included_segments = []
        included_headings = []
        included_footnotes = []
        included_segment_footnotes = []
        included_artifacts = []
        for op in [self.main_opinion] + self.separate_opinions:
            row = asdict(op)
            row.pop("file_statutes")
            row.pop("file_citations")
            opinion_rows.append(row)  # each opinion is added to the collection
            included_statutes.extend(op.statutes)  # each opinion's statutes
            included_citations.extend(op.citations)  # each opinion's citations
            included_segments.extend(op.segments)  # each opinion's segments
            included_headings.extend(op.headings)  # each opinion's headings
            included_footnotes.extend(op.footnotes)  # each opinion's footnotes
            included_segment_footnotes.extend(op.segment_footnotes)
            included_artifacts.extend(op.artifacts)
        return Collection(
            opinions=opinion_rows,
            statutes=included_statutes,
            citations=included_citations,
            headings=included_headings,
            segments=included_segments,
            footnotes=included_footnotes,
            segment_footnotes=included_segment_footnotes,
            artifacts=included_artifacts,
        )

    def create_lines(self, include_regex: str | None = None):
        lines = Line.prep(self.related.segments, include_regex)
        return (line._asdict() for line in lines)

    def create_fns(self, include_regex: str | None = None):
        lines = Line.fn(self.related.footnotes, include_regex)
        return (line._asdict() for line in lines)

    @classmethod
    def from_file(cls, file: Path):
        """Initialize the Decision object based on the _main_ file;
        this may be associated with related _opinion_ files."""
        separate_opinions = []
        opdir = file.parent.joinpath("opinion")
        cat, num, date, _ = file.parts[-4:]
        meta = frontmatter.load(str(file))

        # generate id
        cite = Citation.from_docket_row(
            cat=cat,
            num=num,
            date=date,
            opt_phil=meta.get("phil"),  # type: ignore
            opt_scra=meta.get("scra"),  # type: ignore
            opt_offg=meta.get("offg"),  # type: ignore
        )
        id = cite.set_slug()
        if not id:
            raise Exception("Could not generate decision id.")

        # generate opinions
        if opdir.exists():
            for op_file in opdir.glob("*.md"):
                writer = get_writer_from_path(op_file)
                justice_id = int(writer.justice_digit) if writer.justice_digit else None
                op_filemeta = frontmatter.load(str(op_file))
                phrases = op_filemeta.get("phrases", None)  # type: ignore
                separate_opinions.append(
                    Opinion(
                        id=f"{id}-{file.stem}",
                        decision_id=id,
                        content=op_filemeta.content,
                        justice_id=justice_id,
                        is_main=False,
                        label=op_filemeta.get("label", "Opinion"),  # type: ignore
                        file_statutes=op_filemeta.get("statutes"),  # type: ignore
                        file_citations=op_filemeta.get("citations"),  # type: ignore
                        file_artifacts=Artifact.from_phrases(phrases=phrases),  # type: ignore
                    )
                )

        # create main_opinion
        authorship = get_writer_from_path(file)
        main_opinion = Opinion(
            id=f"{id}-main",
            decision_id=id,
            content=meta.content,
            justice_id=authorship.justice_digit,
            is_main=True,
            label="Main",
            file_statutes=meta.get("statutes"),  # type: ignore
            file_citations=meta.get("citations"),  # type: ignore
            file_artifacts=Artifact.from_phrases(phrases=meta.get("phrases", None)),  # type: ignore
        )

        # create votes
        votes = []
        if votelines := meta.get("votelines"):
            for counter, line in enumerate(votelines, start=1):  # type: ignore
                votes.append(
                    Vote(
                        id=f"{id}-vote-{counter}",
                        opinion_id=main_opinion.id,
                        decision_id=id,
                        text=line,
                        char_count=len(line),
                    )
                )

        # collect all fields
        return cls(
            id=id,
            citation=cite,
            title=meta.get("title"),  # type: ignore
            short=meta.get("short"),  # type: ignore
            main_opinion=main_opinion,
            separate_opinions=separate_opinions,
            justice_id=authorship.justice_digit,
            curiam=authorship.curiam,
            category=meta.get("category"),  # type: ignore
            composition=meta.get("composition"),  # type: ignore
            votes=votes,
        )

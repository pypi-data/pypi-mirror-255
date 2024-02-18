import re
from enum import Enum
from typing import NamedTuple

from .regex import jx

the = r"[Tt][Hh][Ee]"
action = r"([Rr]uling|RULING|Case|[Pp]roceeding|Decision|DECISION|Disposition|Judgment|Order)s?"  # noqa: E501
connect = r"([Oo][Ff]|[Ii][Nn]|[Bb]efore|BEFORE)"
possessive = r"[',’]?s?"
qualified = r"(\s+(Division|\*{0,3}En\sBanc\*{0,3}?))?"


class Court(NamedTuple):
    regex: str  # ME?C?TCC?|(Metropolitan|Municipal)\s+Trial\s+Court)(\s+in\s+Cities)?
    tests: list[str]

    def __repr__(self) -> str:
        return f"<Court: {self.regex[:10]}>"

    @property
    def simple(self) -> str:
        return rf"({the}\s)?(Assailed\s)?({self.regex}){possessive}\s+{action}"

    @property
    def variant(self) -> str:
        return rf"({the}\s)?{action}\s+{connect}\s+({the}\s+)?({self.regex})"

    @property
    def patterns(self):
        return [self.simple, self.variant]

    @property
    def as_phrases(self):
        """See Phrase Enum to follow the format used by the properties."""
        return [[self.simple], [self.variant]]

    def test(self):
        p = re.compile(jx(regexes=self.patterns, border="|"))
        for item in self.tests:
            if not p.fullmatch(item):
                raise Exception(f"{self=} != {item=}")
        return True


class Courts(Enum):
    MTC = Court(
        regex=(
            r"M?C?[Ee]?TCC?|(Metropolitan|Municipal)\s+Trial\s+Court(\s+in\s+Cities)?"
        ),
        tests=[
            "MTC Ruling",
            "MTCC Decision",
            "Ruling of the Municipal Trial Court",
        ],
    )

    RTC = Court(
        regex=r"RTC|([Rr]egional\s+)?[Tt]rial\s+[Cc]ourt",
        tests=[
            "RTC Ruling",
            "RTC's Ruling",
            "Ruling of the Regional Trial Court",
            "Ruling of the Trial Court",
            "The Ruling of the Trial Court",
            "trial court's ruling",
        ],
    )

    CA = Court(
        regex=r"CA|Court\s+of\s+Appeals?|Appellate Court",
        tests=[
            "CA Ruling",
            "CA's Ruling",
            "Ruling of the Court of Appeal",
            "Ruling of the Court of Appeals",
            "Ruling of the Appellate Court",
        ],
    )

    CTA = Court(
        regex=rf"(CTA{qualified})|(Court\s+of\s+Tax\s+Appeals{qualified})",  # noqa: E501
        tests=[
            "CTA Ruling",
            "CTA Division Ruling",
            "CTA En Banc Ruling",
            "CTA's Ruling",
            "Ruling of the Court of Tax Appeals",
            "Ruling of the Court of Tax Appeals Division",
            "Ruling of the Court of Tax Appeals En Banc",
        ],
    )

    SB = Court(
        regex=r"Sandiganbayan|SB",  # noqa: E501
        tests=[
            "Sandiganbayan Ruling",
            "SB Decision",
            "Ruling of the Sandiganbayan",
            "Proceedings before the Sandiganbayan",
        ],
    )

    HLURB = Court(
        regex=r"HLURB",  # noqa: E501
        tests=[
            "HLURB Ruling",
            "HLURB proceedings",
        ],
    )

    COA = Court(
        regex=r"COA|Commission\s+on\s+Audit",  # noqa: E501
        tests=[
            "The COA Ruling",
            "COA Ruling",
            "COA Decision",
            "Ruling of COA",
            "Proceedings before the Commission on Audit",
        ],
    )

    OP = Court(
        regex=r"OP|Office\s+of\s+the\s+President",  # noqa: E501
        tests=[
            "OP Ruling",
            "Ruling of the Office of the President",
        ],
    )

    DAR = Court(
        regex=r"[D|P]ARAB|(Department\s+of|Provincial)\s+Agrarian\s+Reform\s+Adjudicatory\s+Board",  # noqa: E501
        tests=[
            "DARAB Ruling",
            "PARAD Ruling",
        ],
    )

    OMB = Court(
        regex=r"Ombudsman|OMB",  # noqa: E501
        tests=[
            "OMB Ruling",
            "Ombudsman Decision",
            "Ruling of the Ombudsman",
        ],
    )

    NLRC = Court(
        regex=r"National\s+Labor\s+Relations\s+Commission|NLRC",  # noqa: E501
        tests=[
            "NLRC Ruling",
            "NLRC's Decision",
            "Proceedings before the National Labor Relations Commission",
        ],
    )

    LA = Court(
        regex=r"Labor\s+Arbiter|LA",  # noqa: E501
        tests=[
            "LA Ruling",
            "LA's Decision",
            "Ruling of the LA",
        ],
    )

    CSC = Court(
        regex=r"CSC|Civil\s+Service\s+Commission",  # noqa: E501
        tests=[
            "CSC Ruling",
            "CSC's Decision",
            "Ruling of the CSC",
        ],
    )

    COMELEC = Court(
        regex=rf"COMELEC{qualified}|Comelec{qualified}|Commission\s+on\s+Elections{qualified}",  # noqa: E501
        tests=[
            "COMELEC En Banc Ruling",
            "Ruling of the Comelec Division",
            "The Ruling of the COMELEC",
        ],
    )

    CIAC = Court(
        regex=r"CIAC|Construction\s+Industry\s+Arbitration\s+Commission",  # noqa: E501
        tests=[
            "CIAC Ruling",
            "Ruling of the CIAC",
        ],
    )

    @classmethod
    def check(cls):
        for member in cls:
            member.value.test()

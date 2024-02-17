import re
from enum import Enum

from .courts import Courts
from .regex import add_terminal_options, jx


class Phrase(Enum):
    mtc = Courts.MTC.value.as_phrases
    rtc = Courts.RTC.value.as_phrases
    ca = Courts.CA.value.as_phrases
    cta = Courts.CTA.value.as_phrases
    csc = Courts.CSC.value.as_phrases
    coa = Courts.COA.value.as_phrases
    la = Courts.LA.value.as_phrases
    nlrc = Courts.NLRC.value.as_phrases
    sb = Courts.SB.value.as_phrases
    omb = Courts.OMB.value.as_phrases
    ciac = Courts.CIAC.value.as_phrases
    comelec = Courts.COMELEC.value.as_phrases
    op = Courts.OP.value.as_phrases
    dar = Courts.DAR.value.as_phrases
    hlurb = Courts.HLURB.value.as_phrases
    preface = [
        [r"Prefa(ce|tory)"],
    ]
    intro = [
        [
            r"(The\s+)?(Statement\s+of\s+the\s+Facts|Nature|Statement|Facts|Antecedents|Antecedent\s+Facts)",
            r"of",
            r"the",
            r"Case",
        ],
        [
            r"(The\s+)?(Statement\s+of\s+Fact|Antecedent|Case|Fact|Antecedent\s+Fact|Background\s+Fact)s?"  # noqa: E501
        ],
        [
            r"(The\s+)?(Relevant|(Salient\s+)?Factual|Case|Factual\s+and\s+Procedural|Procedural\s+and\s+Factual)?",
            r"(Antecedents?|Background)",
        ],
        [r"The", r"(Essential\s+)?Facts", r"and", r"Antecedent\s+Proceedings"],
        [r"The", r"Case", "and", r"the", r"Facts"],
        [r"The", r"Undisputed", r"Facts"],
    ]
    args = [
        [
            r"(The\s+)?(Version|Arguments|Contentions|Evidence|Position|Comment|Allegations)",
            r"(of|for)",
            r"the",
            r"(Petitioner|Respondent|Prosecution|Defense|Accused)",
        ],
        [
            r"(The\s+)?(Petitioner|Respondent|Prosecution|Defense|Accused)([',’]s)?",
            r"(Version|Arguments|Evidence|Position|Comment|Contentions|Reply|Allegations)",
        ],
        [r"(The\s+)?Arguments?", r"of", r"the", r"Parties"],
    ]
    pleading = [
        [r"(The\s+)?(Present|Instant)", r"(Petition|Appeal)s?(\s+for\s+Review)?"],
        [r"(The\s+)?Petition", r"Before", r"the", r"Court"],
    ]
    issue = [
        [r"(The\s+)?Issues?", r"Before", r"the", r"Court"],
        [r"Issues?", r"of", r"the", r"Case"],
        [r"Issues?", r"and", r"Arguments"],
        [r"(The\s+)?(Question|Issue)s?", r"Presented"],
        [r"Assignments?", r"of", r"Errors?"],
        [r"(The\s*)?(Threshold|Core|Sole|Lone|Assigned)?", r"(Error|Issue)s?"],
        [r"(The\s+)?Issues?"],
    ]
    ruling = [
        [r"(The\s+|\(2\^nd\^\)\s+)?Ruling", r"of", r"t(his|he)", r"Court"],
        [r"T(he|his)", r"Court[',’]s", r"Rulings?"],
        [r"Our", r"Ruling"],
        [r"Court[',’]s", r"Ruling"],
        [r"(II|III|IV|V|VI)\.", r"Ruling"],
        [r"(Ruling|Discussion)"],
    ]
    judgment = [
        [r"((The\s+)?Judgment|Fallo|Disposition)"],
    ]
    misc = [
        [r"Proceedings", r"[B|b]efore", r"the", r"Court"],
    ]
    oca = [
        [r"OCA[',’]?s?", r"Action", r"and", r"Recommendations?"],
        [r"(The\s+)?IBP", r"Proceedings"],
        [
            r"(The\s+)?(Action|Findings)",
            r"and",
            r"Recommendations?",
            r"of",
            r"the",
            r"OCA",
        ],
        [
            r"Recommendations?",
            r"of",
            r"the",
            r"OCA",
        ],
        [
            r"(The\s+)Action",
            r"and",
            r"Recommendation?",
            r"of",
            r"the",
            r"Office",
            r"of",
            r"the",
            r"Court",
            r"Administrator",
        ],
    ]
    ibp = [
        [r"IBP[',’]?s?", r"Report", r"and", r"Recommendations?"],
        [r"(The\s+)?IBP", r"Proceedings"],
        [
            r"Report",
            r"and",
            r"Recommendations?",
            r"of",
            r"the",
            r"Integrated",
            r"Bar",
            r"of",
            r"the",
            r"Philippines",
        ],
    ]

    @property
    def regex(self):
        """Each member pattern consists of a list of strings. Each string
        will be joined as an option to create the full regex string for
        each member."""
        return jx(
            regexes=[rf"{add_terminal_options(jx(regex))}" for regex in self.value],
            border="|",
            enclose=True,
        )

    @classmethod
    def generate_regex_unnamed(cls) -> str:
        """Helpful in both programmatic searchers (see format.py) and in
        generating the full regex string for manual vscode searches."""
        return jx(
            regexes=[member.regex for member in cls],
            border="|",
            enclose=True,
        )

    @classmethod
    def generate_regex_named(cls) -> str:
        return jx(
            regexes=[rf"(?P<{member.name}>{member.regex})" for member in cls],
            border="|",
            enclose=True,
        )

    @classmethod
    def compiler(cls) -> re.Pattern[str]:
        """Using the full regex string for each member, create named patterns
        using the member name. This ought to be compiled only once so that
        it need not create patterns every single time."""
        return re.compile(cls.generate_regex_named(), re.I)

    @classmethod
    def searcher(cls) -> str:
        return rf"\*+{Phrase.generate_regex_unnamed()}):?\*+"


headers = Phrase.compiler()


def categorize_header(text: str):
    if text := text.strip():
        if match := headers.fullmatch(text):
            for k, v in match.groupdict().items():
                if v:
                    return k

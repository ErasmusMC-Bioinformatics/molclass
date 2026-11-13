from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings

from sources import *
from util import get_release_tag, get_release_year


class Settings(BaseSettings):
    debug: bool = True
    port: int = 8080
    release_tag: str = Field(get_release_tag())
    release_year: int = Field(get_release_year())
    disabled_sources: str = Field(default="", env="DISABLED_SOURCES")

    sources: List[type] = [
        # is_banner()=True sources should be at the start, they are shown above the cards
        Table3,
        GenomeNexus,
        InHouse,
        GeneLists,
        Alamut,
        COSMIC,
        ClinVar,
        Franklin,
        CKB,
        TP53,
        LOVD,
        AlphaGenome,
        OncoKB,
        cBioPortal,
        Varsome,
        Mutalyzer,
        Mastermind,
        SpliceAI,
        BoostDM,
        HMF,
        # is_hidden()=True sources should be at the end, to not leave gaps in source layout
        Clingen,
        Ensembl,
        # GnomAD,
        dbSNP,
    ]

    # the sources of a stack are shown on top of each other in one column, at the place of the first of them in sources
    stacked_sources: List[List[type]] = [
        [InHouse, AlphaGenome],
        [Alamut, Franklin, CKB],
    ]

    # the width of a source on the page in twelfths of the page, a source that is not listed gets 4 (a third).
    # A stack has the width of the first source in its list, also when that source is switched off
    source_widths: dict = {
        "GenomeNexus": 6,
        "InHouse": 3,
        "Alamut": 3,
    }

    # the order of the links on the Links card: the names of the is_link()=True sources and of the shared links
    links_order: List[str] = [
        "CKB",
        "SpliceAI",
        "cBioPortal",
        "COSMIC",
        "BoostDM",
    ]

    # all the sources above, also the ones that are switched off, so a stack keeps its place on the page
    configured_sources: List[type] = []

    def __init__(self):
        super().__init__()
        self.configured_sources = list(self.sources)
        disabled_sources_list = self.disabled_sources.split(",")
        self.sources = [
            source
            for source in self.sources
            if source.is_complete(source)
            and source.__name__ not in disabled_sources_list
        ]


settings = Settings()

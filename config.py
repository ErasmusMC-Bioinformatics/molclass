from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings

from sources import *
from util import get_release_tag


class Settings(BaseSettings):
    debug: bool = True
    port: int = 8080
    release_tag: str = Field(get_release_tag())

    sources: List[type] = [
        GenomeNexus,
        GeneLists,
        Alamut,
        COSMIC,
        ClinVar,
        Franklin,
        CKB,
        LOVD,
        OncoKB,
        cBioPortal,
        Varsome,
        HMF,
        Mutalyzer,
        SpliceAI,
        BoostDM,
        # is_hidden()=True sources should be at the end, to not leave gaps in source layout
        Clingen,
        Ensembl,
        # GnomAD,
        dbSNP,
        TP53,
    ]

    def __init__(self):
        super().__init__()
        self.sources = [source for source in self.sources if source.is_complete(source)]


settings = Settings()

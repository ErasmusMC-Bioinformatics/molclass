from typing import List
from pydantic import BaseSettings, Field

from sources import *

class Settings(BaseSettings):
    debug: bool = Field(True, env="DEBUG")
    port: int = Field(8080, env="PORT")

    sources: List[type] = [
        Alamut,
        dbSNP,
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
        # Mastermind,
        TP53,
        # is_hidden()=True sources should be at the end, to not leave gaps in source layout
        Clingen,
        # GnomAD,
    ]

    def __init__(self):
        super().__init__()
        self.sources = [source for source in self.sources if source.is_complete(source)]

settings = Settings()
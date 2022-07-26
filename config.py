from typing import List, Tuple
from pydantic import BaseSettings, Field

from typing import Callable
from sources import Alamut
from sources import dbSNP
from sources import Franklin
from sources import COSMIC
from sources import ClinVar
from sources import LOVD
from sources import cBioPortal
from sources import CKB
from sources import OncoKB
from sources import PMKB
from sources import TP53
from sources import Varsome
from sources import HMF

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
        TP53,
        # PMKB,
    ]

settings = Settings()
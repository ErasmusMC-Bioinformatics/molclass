from typing import List, Tuple
from pydantic import BaseSettings, Field

from typing import Callable
from sources import Alamut
from sources import dbSNP
from sources import Franklin
from sources import Cosmic
from sources import Clinvar
from sources import Lovd
from sources import CBioPortal
from sources import CKB
from sources import OncoKB
from sources import PMKB
from sources import TP53
from sources import Varsome

class Settings(BaseSettings):
    debug: bool = Field(True, env="DEBUG")
    port: int = Field(8080, env="PORT")

    sources: List[type] = [
        Alamut,
        CKB,
        dbSNP,
        CBioPortal,
        Franklin,
        Cosmic,
        Clinvar,
        OncoKB,
        Lovd,
        PMKB,
        TP53,
        Varsome
    ]

settings = Settings()
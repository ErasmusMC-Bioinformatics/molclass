from typing import List
from pydantic import BaseSettings, Field

from typing import Callable
from sources import NCBI
from sources import dbSNP
from sources import Franklin
from sources import Cosmic
from sources import Clinvar
from sources import Clinvar_Miner
from sources import lovd
from sources import Alamut
from sources import CBioPortal
from sources import CKB
from sources import OncoKB
from sources import PMKB
from sources import TP53

# https://pmkb.weill.cornell.edu/search?utf8=%E2%9C%93&search=TSC1

class Settings(BaseSettings):
    debug: bool = Field(True, env="DEBUG")
    port: int = Field(8080, env="PORT")

    sources: List[Callable] = [
        Alamut,
        CKB,
        dbSNP,
        CBioPortal,
        Franklin,
        Cosmic,
        Clinvar,
        OncoKB,
        lovd,
        PMKB,
        TP53
    ]

settings = Settings()
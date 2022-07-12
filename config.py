from typing import List, Tuple
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

from sources.dbsnp import dbSNP_entries
from sources.clinvar import clinvar_entries
from sources.pmkb import PMKB_entries
from sources.franklin import Franklin_entries

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

    entries = {
        "dbSNP": dbSNP_entries,
        "Clinvar": clinvar_entries,
        "PMKB": PMKB_entries,
        "Franklin": Franklin_entries
    }

settings = Settings()
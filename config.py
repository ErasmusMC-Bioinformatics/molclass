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

from sources.dbsnp import _dbSNP
from sources.clinvar import _Clinvar
from sources.pmkb import _PMKB
from sources.franklin import _Franklin

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

    entries = [
        _Franklin,
        _dbSNP,
        _PMKB,
        _Clinvar
    ]

settings = Settings()
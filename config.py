from typing import List, Tuple
from pydantic import BaseSettings, Field

from typing import Callable
from sources import NCBI
from sources import dbSNP
from sources import Franklin
from sources import Cosmic
from sources import Clinvar
from sources import Clinvar_Miner
from sources import Lovd
from sources import CBioPortal
from sources import CKB
from sources import OncoKB
from sources import PMKB
from sources import TP53

from sources.dbsnp import dbSNP
from sources.clinvar import Clinvar
from sources.pmkb import PMKB
from sources.franklin import Franklin
from sources.alamut import Alamut
from sources.cbioportal import CBioPortal
from sources.ckb import CKB
from sources.cosmic import Cosmic
from sources.lovd import Lovd
from sources.oncokb import OncoKB
from sources.tp53 import TP53

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
        Lovd,
        PMKB,
        TP53
    ]

    entries = [
        Alamut,
        CKB,
        CBioPortal,
        Franklin,
        Cosmic,
        dbSNP,
        OncoKB,
        Lovd,
        PMKB,
        Clinvar,
        TP53
    ]

settings = Settings()
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

class Settings(BaseSettings):
    debug: bool = Field(True, env="DEBUG")
    port: int = Field(8080, env="PORT")

    sources: List[Callable] = [
        #NCBI,
        dbSNP,
        Alamut,
        Franklin,
        Cosmic,
        Clinvar,
        Clinvar_Miner,
        lovd,
        CBioPortal,
        CKB,
    ]

settings = Settings()
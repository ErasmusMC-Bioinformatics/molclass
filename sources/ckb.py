import re

from bs4 import BeautifulSoup
from yarl import URL

from templates import templates

from .source_result import Source, SourceURL
from util import get_pdot_abbreviation

from pydantic import BaseSettings, Field

class Secrets(BaseSettings):
    ckb_user: str = Field(default=None, env="CKB_USER")
    ckb_pass: str = Field(default=None, env="CKB_PASSWORD")

secrets = Secrets()

class CKB(Source):
    def set_entries(self):
        self.entries = {
            ("gene", ): self.gene,
        }

    async def ckb_login(self) -> bool:
        """
        Login to ckb, the logged in session is stored in the aiohttp session, 
        so no need to pass around tokens or anything
        """
        ckb_login_url = f"https://ckbhome.jax.org/login/authenticate"
        login_data = {
            "username": secrets.ckb_user,
            "password": secrets.ckb_pass,
        }
        resp, login_html = await self.async_post_text(ckb_login_url, data=login_data)
        print("logged in: ", "not able to find a user with that email and password" not in login_html)
        print(secrets.ckb_user, secrets.ckb_pass)
        return "not able to find a user with that email and password" not in login_html

        # get cookies so we can reuse them
        # print(self.session.cookie_jar.filter_cookies(URL("https://ckbhome.jax.org"))["GCLB"])

    async def gene(self):
        """
        Scrape the gene grid page of CKB to get the url to that genes page
        """
        gene = self.variant["gene"]

        url = "https://ckbhome.jax.org/gene/grid"
        resp, gene_html = await self.async_get_text(url, ssl=False)
        if resp.status != 200:
            self.log_warning(f"Could not load gene page: {resp.status}")
            self.html_links["main"] = SourceURL("Gene", url)
            return 

        # use a BeautifulSoup regex query to search for the html <a> element with the gene name
        soup = BeautifulSoup(gene_html, features="html.parser")
        gene_link = soup.find("a", text=re.compile(f"\s*[^\w]{gene}\s*"))

        if not gene_link:
            self.log_warning("Gene not found in ckb gene list")
            self.found = False
            return

        url = f"https://ckbhome.jax.org{gene_link['href']}"
        self.html_links["main"] = SourceURL("Gene", url)
        
        if "pdot" in self.variant:
            pdot = get_pdot_abbreviation(self.variant["pdot"])
            pdot = pdot[2:]  # cut off 'p.'
            pdot = pdot.replace("*", "\*")  # escape '*'
            self.html_text = f"Manually search for {pdot} on gene page!"
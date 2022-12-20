import re

from bs4 import BeautifulSoup
from yarl import URL

from templates import templates

from .source_result import Source, SourceURL
from util import get_pdot_abbreviation

from pydantic import BaseSettings, Field

class Secrets(BaseSettings):
    ckb_user: str = Field(None, env="CKB_USER")
    ckb_pass: str = Field(None, env="CKB_PASSWORD")

secrets = Secrets()

class CKB(Source):
    def set_entries(self):
        self.entries = {
            ("gene", ): self.gene,
        }

    async def ckb_login(self) -> bool:
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
        gene = self.variant["gene"]

        url = "https://ckbhome.jax.org/gene/grid"
        resp, gene_html = await self.async_get_text(url, ssl=False)
        if resp.status != 200:
            self.log_warning(f"Could not load gene page: {resp.status}")
            self.html_links["main"] = SourceURL("Gene", url)
            return 

        soup = BeautifulSoup(gene_html, features="html.parser")

        gene_link = soup.find("a", text=re.compile(f"\s*[^\w]{gene}\s*"))

        if not gene_link:
            self.log_warning("Gene not found in ckb gene list")
            self.found = False
            return

        url = f"https://ckbhome.jax.org{gene_link['href']}"
        self.html_links["main"] = SourceURL("Gene", url)
        
        pdot = get_pdot_abbreviation(self.variant["pdot"])
        pdot = pdot[2:]  # cut off 'p.'
        pdot = pdot.replace("*", "\*")  # escape '*'
        self.html_text = f"Manually search for {pdot} on gene page!"
        return

        if "pdot" not in self.variant:
            self.log_info("No pdot, can't find variant page")
            return

        resp, gene_html = await self.async_get_text(url)
        was_redirected = 302 in [history.status for history in resp.history]
        if was_redirected:  # redirect to login page
            self.log_info("Logged out, logging in again for Boost")
            with open("./ckb.html", 'w') as ckb_html:
                ckb_html.write(gene_html)
            logged_in = await self.ckb_login()
            if not logged_in:
                self.matches_consensus_tooltip.append(f"Could not login to CKB Boost, variant might exist")
                self.log_error("Could not login to CKB Boost")
            resp, gene_html = await self.async_get_text(url)
            with open("./ckb.html", 'w') as ckb_html:
                ckb_html.write(gene_html)

        was_redirected = 302 in [history.status for history in resp.history]
        if was_redirected:  # redirect to login page
            self.log_info("Logged out again uhoh")

        if resp.status != 200:
            self.log_warning(f"Could not load gene page: {resp.status}")
            return

        pdot = get_pdot_abbreviation(self.variant["pdot"])
        pdot = pdot[2:]  # cut off 'p.'
        pdot = pdot.replace("*", "\*")  # escape '*'
        
        soup = BeautifulSoup(gene_html, features="html.parser")

        variant_link = soup.find("a", string=re.compile(f".*{pdot}.*"))
        variant_link = soup.select_one(f"a:contains('{pdot}')")

        if not variant_link:
            self.log_warning(f"Variant {pdot} not found in variant list")
            self.html_text = f"Variant {pdot} not Found"
            self.found = False
            return
        
        self.html_links["gene"] = SourceURL("Gene", url)

        url = f"https://ckbhome.jax.org{variant_link['href']}"
        self.html_links["main"] = SourceURL("Variant", url)

        self.complete = True
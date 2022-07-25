import re

from bs4 import BeautifulSoup

from templates import templates

from .source_result import Source, SourceURL
from util import get_pdot_abbreviation

class CKB(Source):
    def set_entries(self):
        self.entries = {
            ("gene", ): self.gene,
        }

    async def gene(self):
        gene = self.variant["gene"]

        url = "https://ckb.jax.org/gene/grid"
        resp, gene_html = await self.async_get_text(url)
        if resp.status != 200:
            self.log_warning(f"Could not load gene page: {resp.status}")
            self.html_links["main"] = SourceURL("Go", url)
            return 

        soup = BeautifulSoup(gene_html, features="html.parser")

        gene_link = soup.find("a", text=re.compile(f"\s*{gene}\s*"))

        if not gene_link:
            self.log_warning("Gene not found in ckb gene list")
            self.found = False
            return

        url = f"https://ckb.jax.org{gene_link['href']}"
        self.html_links["main"] = SourceURL("Go", url)

        if "pdot" not in self.variant:
            self.log_info("No pdot, can't find variant page")
            return

        resp, gene_html = await self.async_get_text(url)

        if resp.status != 200:
            self.log_warning(f"Could not load gene page: {resp.status}")
            return

        pdot = get_pdot_abbreviation(self.variant["pdot"])
        pdot = pdot[2:]  # cut off 'p.'
        pdot = pdot.replace("*", "\*")  # escape '*'
        
        soup = BeautifulSoup(gene_html, features="html.parser")
        variant_link = soup.find("a", text=re.compile(f"\s+{pdot}\s+"))

        if not variant_link:
            self.log_warning(f"Variant {pdot} not found in variant list")
            return
        
        self.html_links["gene"] = SourceURL("Gene", url)

        url = f"https://ckb.jax.org{variant_link['href']}"
        self.html_links["main"] = SourceURL("Go", url)

        self.complete = True
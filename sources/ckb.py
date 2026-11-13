import re
import time

from pydantic_settings import BaseSettings

from .source_result import Source, SourceURL


class Secrets(BaseSettings):
    ckb_user: str | None = None
    ckb_password: str | None = None

secrets = Secrets()

GENE_GRID_URL = "https://ckbhome.jax.org/gene/grid"
GENE_LINK_RE = re.compile(r'<a[^>]*href="(/gene/show[^"]*)"[^>]*>([^<]*)</a>')

# the page with all the genes of CKB is big and slow, so it is only retrieved once a day
GENES_MAX_AGE = 24 * 60 * 60
_genes: tuple[float, dict[str, str]] = (0, {})

class CKB(Source):
    def is_link(self) -> bool:
        return True

    def set_entries(self):
        self.entries = {
            ("transcript", ): self.transcript,
            ("gene", ): self.gene,
        }

    async def ckb_login(self) -> bool:
        """
        Login to ckb, the logged in session is stored in the aiohttp session, 
        so no need to pass around tokens or anything
        """
        ckb_login_url = "https://ckbhome.jax.org/login/authenticate"
        login_data = {
            "username": secrets.ckb_user,
            "password": secrets.ckb_password,
        }
        _, login_html = await self.async_post_text(ckb_login_url, data=login_data)
        return "not able to find a user with that email and password" not in login_html

        # get cookies so we can reuse them
        # print(self.session.cookie_jar.filter_cookies(URL("https://ckbhome.jax.org"))["GCLB"])

    async def get_genes(self) -> dict[str, str] | None:
        """
        Scrape the gene grid page of CKB, returns {gene: url of the page of the gene}. None if the page can't be loaded
        """
        global _genes
        if not _genes[1] or time.time() - _genes[0] > GENES_MAX_AGE:
            resp, gene_html = await self.async_get_text(GENE_GRID_URL, ssl=False)
            if resp.status != 200:
                self.log_warning(f"Could not load gene page: {resp.status}")
                return _genes[1] or None
            genes = {gene.strip().upper(): f"https://ckbhome.jax.org{href}" for href, gene in GENE_LINK_RE.findall(gene_html)}
            if genes:
                _genes = (time.time(), genes)
        return _genes[1] or None

    async def transcript(self):
        """
        Looks up the gene of the transcript, so the link is shown without waiting for another source to supply the gene
        """
        gene = await self.resolve_gene()
        if gene:
            await self.report(gene)
            self.complete = True

    async def gene(self):
        await self.report(self.variant["gene"])
        self.complete = True

    async def report(self, gene):
        """
        Adds the url of the CKB page of the gene
        """
        genes = await self.get_genes()
        if genes is None:
            self.html_links["main"] = SourceURL("Gene", GENE_GRID_URL)
            return

        url = genes.get(str(gene).upper())
        if not url:
            self.log_warning("Gene not found in ckb gene list")
            self.found = False
            return

        self.html_links["main"] = SourceURL("Gene", url)

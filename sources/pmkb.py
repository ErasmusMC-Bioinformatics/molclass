import aiohttp
from .source_result import Source

class PMKB(Source):
    def set_entries(self):
        self.entries = {
            ("gene",): self.gene
        }

    async def gene(self):
        gene = self.variant["gene"]

        url = f"https://pmkb.weill.cornell.edu/search?search={gene}"
        self.set_html(title="PMKB", text="", subtitle="", links=[{"url": url, "text": "Go"}])
        self.complete = True
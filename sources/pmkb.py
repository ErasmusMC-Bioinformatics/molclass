import aiohttp
from .source_result import Source, SourceURL

class PMKB(Source):
    def set_entries(self):
        self.entries = {
            ("gene",): self.gene
        }

    async def gene(self):
        gene = self.variant["gene"]

        url = f"https://pmkb.weill.cornell.edu/search?search={gene}"

        self.html_links["main"] = SourceURL("Go", url)
        self.complete = True
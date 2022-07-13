from .source_result import Source

class OncoKB(Source):
    def set_entries(self):
        self.entries = {
            ("gene", ): self.gene,
        }

    async def gene(self):
        gene = self.variant["gene"]
        url = f"https://www.oncokb.org/gene/{gene}"

        self.set_html(links=[{"url": url, "text": "Go"}])
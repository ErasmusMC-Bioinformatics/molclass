from .source_result import Source, SourceURL

class OncoKB(Source):
    def set_entries(self):
        self.entries = {
            ("gene", ): self.gene,
        }

    async def gene(self):
        gene = self.variant["gene"]
        url = f"https://www.oncokb.org/gene/{gene}"

        self.html_links["main"] = SourceURL("Go", url)
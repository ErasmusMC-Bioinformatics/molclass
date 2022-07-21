from .source_result import Source, SourceURL


class COSMIC(Source):
    def set_entries(self):
        self.entries = {
            ("gene", ): self.gene,
        }

    async def gene(self):
        gene = self.variant["gene"]
        
        url = f"https://cancer.sanger.ac.uk/cosmic/gene/analysis?ln={gene}"

        self.html_links["main"] = SourceURL("Go", url)

from .source_result import Source, SourceURL

class Mastermind(Source):
    def set_entries(self):
        self.entries = {
            ("gene", "pdot"): self.gene_pdot,
        }
    
    async def gene_pdot(self):
        gene = self.variant["gene"]
        pdot = self.variant["pdot"]

        url = f"https://mastermind.genomenon.com/detail?mutation={gene}:{pdot}"
        self.html_links["main"] = SourceURL("Go", url)
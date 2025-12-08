from .source_result import Source, SourceURL

class BoostDM(Source):
    def set_entries(self):
        self.entries = {
            ("gene",): self.gene,
        }

    async def gene(self):
        """
        Simply add a URL to the gene
        """
        gene = self.variant["gene"]

        url = f"https://www.intogen.org/boostdm/search?gene={gene}"
        self.html_links["main"] = SourceURL(f"{gene}", url)

    def get_name(self):
        return "BoostDM"
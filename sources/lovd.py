
from .source_result import Source, SourceURL

class LOVD(Source):
    def set_entries(self):
        self.entries = {
            ("gene", ): self.gene,
        }

    async def gene(self):
        gene = self.variant["gene"]
        url = f"https://databases.lovd.nl/shared/variants/{gene}/unique"

        self.html_links["main"] = SourceURL("Go", url)
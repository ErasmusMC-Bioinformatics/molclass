
from .source_result import Source

class Lovd(Source):
    def set_entries(self):
        self.entries = {
            ("gene", ): self.gene,
        }

    async def gene(self):
        gene = self.variant["gene"]
        url = f"https://databases.lovd.nl/shared/variants/{gene}/unique"

        self.set_html(title="LovD", text="", subtitle="", links=[{"url": url, "text": "Go"}])
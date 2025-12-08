import urllib.parse

from .source_result import Source, SourceURL

class SpliceAI(Source):
    def set_entries(self):
        self.entries = {
            ("transcript", "cdot"): self.transcript_cdot,
        }

    async def transcript_cdot(self):
        """
        Simply add a URL to the transcript_cdot
        """
        transcript = self.variant["transcript"]
        cdot = self.variant["cdot"]
        query = f"{transcript}:{cdot}"
        enc_query = urllib.parse.quote(query)

        url = f"https://spliceailookup.broadinstitute.org/#variant={enc_query}&hg=37&bc=basic&distance=500&mask=0&ra=0"
        self.html_links["main"] = SourceURL(f"{query}", url)

    def get_name(self):
        return "SpliceAI"
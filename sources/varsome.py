
from .source_result import Source, SourceURL

class Varsome(Source):
    def set_entries(self):
        self.entries = {
            ("rs",): self.rs,
            ("transcript", "cdot"): self.transcript_cdot
        }

    async def rs(self):
        rs = self.variant["rs"]
        url = f"https://varsome.com/variant/search?query={rs}&genome=hg19&annotation-mode=germline"
        
        self.html_links["rs"] = SourceURL("RS", url)

    async def transcript_cdot(self):
        transcript = self.variant['transcript']
        cdot = self.variant['cdot']
        transcript_cdot = f"{transcript}:{cdot}"
        url = f"https://varsome.com/variant/search?query={transcript_cdot}&genome=hg19&annotation-mode=germline"
        self.html_links["transcript cdot"] = SourceURL("Transcript:cdot", url)


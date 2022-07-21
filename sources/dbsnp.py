import re

from fastapi.templating import Jinja2Templates

from .source_result import Source, SourceURL

templates = Jinja2Templates(directory="templates")

# https://regex101.com/r/hXBBK8/1
ALLELES_RE = re.compile("<dt>\s*Alleles</dt>[\s\n]+<dd>([^<]+)</dd>", re.IGNORECASE)

GENE_CONSEQUENCE_RE = re.compile("<dt>Gene\s*:\s*Consequence</dt>\s*<dd>\s*<span>(?P<gene>[^ ]+)\s*:\s*(?P<consequence>[^<]+)")

class dbSNP(Source):
    def set_entries(self):
        self.entries = {
            ("rs",): self.rs
        }

    def process(self, text):
        allele_match = ALLELES_RE.search(text)
        if allele_match:
            allele_match = allele_match.group(1)
            ref, alt = allele_match.strip().split(">")[:2]
            self.new_variant_data["ref"] = ref
            self.new_variant_data["alt"] = alt

        self.html_links["main"] = SourceURL("Go", self.url)
        self.html_subtitle = self.variant.get("rs", "-")

        if m := GENE_CONSEQUENCE_RE.search(text):
            self.new_variant_data.update(**m.groupdict())

        self.complete = True



    async def rs(self):
        rs = self.variant["rs"]
        self.url = f"https://www.ncbi.nlm.nih.gov/snp/{rs}"
        response, text = await self.async_get_text(self.url)

        self.process(text)    
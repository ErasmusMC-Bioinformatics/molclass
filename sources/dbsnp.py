import re

from fastapi.templating import Jinja2Templates
from bs4 import BeautifulSoup

from .source_result import Source

templates = Jinja2Templates(directory="templates")

# https://regex101.com/r/hXBBK8/1
ALLELES_RE = re.compile("<dt>\s*Alleles</dt>[\s\n]+<dd>([^<]+)</dd>", re.IGNORECASE)


class dbSNP(Source):
    def set_entries(self):
        self.entries = {
            ("rs",): self.rs
        }

    def process(self, text):
        soup = BeautifulSoup(text, "html.parser")

        clinical_sign_table = soup.find("table", {"id": "clinical_significance_datatable"})
        clinical_sign_tbody = clinical_sign_table.find("tbody")

        card_text = ""
        for row in clinical_sign_tbody.find_all("tr"):
            cols = row.find_all("td")
            cols = [e.text.strip() for e in cols]

            card_text += f"""<a href="https://www.ncbi.nlm.nih.gov/clinvar/{cols[0]}/">{cols[2]}</a><br />"""
        
        allele_match = ALLELES_RE.search(text)
        if allele_match:
            allele_match = allele_match.group(1)
            ref, alt = allele_match.strip().split(">")[:2]
            self.new_variant_data["ref"] = ref
            self.new_variant_data["alt"] = alt

        self.set_html(title="dbSNP", text=card_text, subtitle=self.variant.get("rs", "-"), links=[{"url": self.url, "text": "Go"}])
        self.complete = True


    async def rs(self):
        rs = self.variant["rs"]
        self.url = f"https://www.ncbi.nlm.nih.gov/snp/{rs}"
        text = await self.async_get_text(self.url)

        self.process(text)    
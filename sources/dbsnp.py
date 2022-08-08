import re
from bs4 import BeautifulSoup

from fastapi.templating import Jinja2Templates
from jinja2 import BaseLoader, Environment

from .source_result import Source, SourceURL

templates = Jinja2Templates(directory="templates")

# https://regex101.com/r/hXBBK8/1
ALLELES_RE = re.compile("<dt>\s*Alleles</dt>[\s\n]+<dd>([^<]+)</dd>", re.IGNORECASE)

GENE_CONSEQUENCE_RE = re.compile("<dt>Gene\s*:\s*Consequence</dt>\s*<dd>\s*(<div>|<span>)(?P<gene>[^ ]+)\s*:\s*(?P<consequence>[^<]+)", re.IGNORECASE)

FREQ_TABLE_TEMPLATE = """
<table class='table'>
    <thead>
        <tr>
            <th>Study</th>
            <th>Samples</th>
            <th>Ref</th>
            <th>Alts</th>
        </tr>
    </thead>
{% for _, row in freq_dict.items() %}
    <tbody>
        <tr>
            <td>{{ row.study }}</td>
            <!--<td>{{ row.population }}</td>-->
            <td>{{ row.size }}</td>
            <td>{{ row.ref }}</td>
            <td>{{ row.alts }}</td>
        </tr>
    </tbody>
{% endfor %}
</table>
"""

class dbSNP(Source):
    def set_entries(self):
        self.entries = {
            ("rs",): self.rs
        }

    def get_freq_table(self, dbsnp_text):
        soup = BeautifulSoup(dbsnp_text, "html.parser")

        freq_table_div = soup.find("table", {"id": "dbsnp_freq_datatable"})
        if not freq_table_div:
            self.log_info("No Clinical sign table")
            return ""
        clinical_sign_tbody = freq_table_div.find("tbody")

        freq_dict = {}
        for row in clinical_sign_tbody.find_all("tr"):
            cols = row.find_all("td")
            study, population, group, size, ref, alts = [e.text.strip() for e in cols]
            if population not in ["Global", "Total"]:
                continue
            
            freq_dict[(study, population)] = {
                "study": study,
                "population": population,
                "group": group,
                "size": size,
                "ref": ref,
                "alts": alts,
            }            

        template = Environment(loader=BaseLoader).from_string(FREQ_TABLE_TEMPLATE)
        return template.render(freq_dict=freq_dict)

    async def process(self, text):
        """
        allele_match = ALLELES_RE.search(text)
        if allele_match:
            allele_match = allele_match.group(1)
            ref, alt = allele_match.strip().split(">")[:2]
            self.new_variant_data["ref"] = ref
            self.new_variant_data["alt"] = alt
        """
        self.html_links["main"] = SourceURL("Go", self.url)
        self.html_subtitle = self.variant.get("rs", "-")

        if m := GENE_CONSEQUENCE_RE.search(text):
            self.new_variant_data.update(**m.groupdict())

        resp, dbsnp_text = await self.async_get_text(self.url)
        self.html_text = self.get_freq_table(dbsnp_text)

        self.complete = True



    async def rs(self):
        rs = self.variant["rs"]
        self.url = f"https://www.ncbi.nlm.nih.gov/snp/{rs}"
        response, text = await self.async_get_text(self.url)

        await self.process(text)    
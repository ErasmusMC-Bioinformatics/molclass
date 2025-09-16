import re
from bs4 import BeautifulSoup

from fastapi.templating import Jinja2Templates
from jinja2 import BaseLoader, Environment

from .source_result import Source, SourceURL

templates = Jinja2Templates(directory="templates")

# https://regex101.com/r/hXBBK8/1
ALLELES_RE = re.compile(r"<dt>\s*Alleles</dt>[\s\n]+<dd>([^<]+)</dd>", re.IGNORECASE)

GENE_CONSEQUENCE_RE = re.compile(r"<dt>Gene\s*:\s*Consequence</dt>\s*<dd>\s*(<div>|<span>)(?P<gene>[^ ]+)\s*:\s*(?P<consequence>[^<]+)", re.IGNORECASE)

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
    <tbody>
    {% for row in freq_list %}
        <tr>
            <td>{{ row.study }}</td>
            <!--<td>{{ row.population }}</td>-->
            <td>{{ row.size }}</td>
            <td>{{ row.ref }}</td>
            <td>{{ row.alts }}</td>
        </tr>
    {% else %}
        <tr>
            <td class="text-muted" colspan="4">No Frequencies >= 0.001</td>
        </tr>
    {% endfor %}
    </tbody>
</table>
"""

class dbSNP(Source):
    def set_entries(self):
        self.entries = {
            ("rs",): self.rs
        }

    def min_freq_for_display(self, alts) -> bool:
        for alt in alts.split(","):
            try:
                alt_freq = float(alt[alt.find("=")+1:])
                if alt_freq >= 0.001:
                    return True
            except ValueError:
                return False
        return False

    def get_freq_table(self, dbsnp_text):
        """
        Parses the HTML page to create a frequency table with FREQ_TABLE_TEMPLATE
        """
        soup = BeautifulSoup(dbsnp_text, "html.parser")

        freq_table_div = soup.find("table", {"id": "dbsnp_freq_datatable"})
        if not freq_table_div:
            self.log_info("No Clinical sign table")
            return ""
        clinical_sign_tbody = freq_table_div.find("tbody")

        freq_list = []
        for row in clinical_sign_tbody.find_all("tr"):
            cols = row.find_all("td")
            study, population, group, size, ref, alts = [e.text.strip() for e in cols]
            if population not in ["Global", "Total"]:
                continue
            
            if not self.min_freq_for_display(alts):
                continue
            
            freq_list.append({
                "study": study,
                "population": population,
                "group": group,
                "size": size,
                "ref": ref,
                "alts": alts,
            })

        # sort list by highest alt freq
        freq_list = sorted(freq_list, key=lambda f:  int(f["size"]), reverse=True)
        # freq_list = sorted(freq_list, key=lambda f:  max(f["size"].split(","), key=lambda v: float(v[v.find("=")+1:])), reverse=True)
        if len(freq_list) > 3:
            freq_list = freq_list[:3]

        template = Environment(loader=BaseLoader()).from_string(FREQ_TABLE_TEMPLATE)
        return template.render(freq_list=freq_list)

    async def process(self, text):
        """
        Gets the rs# page from ncbi and parses some meta data from it
        """
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

        _, dbsnp_text = await self.async_get_text(self.url)
        self.html_text = self.get_freq_table(dbsnp_text)

        self.complete = True



    async def rs(self):
        rs = self.variant["rs"]
        self.url = f"https://www.ncbi.nlm.nih.gov/snp/{rs}"
        _, text = await self.async_get_text(self.url)

        await self.process(text)

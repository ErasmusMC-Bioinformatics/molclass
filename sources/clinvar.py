import re
import html
from collections import defaultdict

from bs4 import BeautifulSoup
from jinja2 import Environment, BaseLoader

from .source_result import Source, SourceURL

# https://regex101.com/r/Hxag8o/1
HEADER_RE = re.compile(f"(?P<transcript>NM_?[0-9]+([.][0-9]+)?)[(](?P<gene>[^)]+)[)]:(?P<cdot>c[.](?P<cdot_pos>[0-9*]+([_+-][0-9]+(-[0-9]+)?)?)(?P<cdot_from>[actg]+)?(?P<type>&gt;|[>]|del|ins)(?P<cdot_to>[actg]+))(?P<pdot>\s*[(]p[.](?P<pdot_from>[^0-9]+)(?P<pdot_pos>[0-9]+)(?P<pdot_to>[^\s\n]+))?", re.IGNORECASE)

RS_RE = re.compile("(?P<rs>rs[0-9]+)", re.IGNORECASE)
RS_URL_RE = re.compile(f"https://www.ncbi.nlm.nih.gov/snp/{RS_RE.pattern}")

CLINGEN_RE = re.compile("http://reg.clinicalgenome.org/redmine/projects/registry/genboree_registry/by_caid[?]caid=(?P<id>CA[0-9]+)", re.IGNORECASE)

# https://regex101.com/r/z4NYRj/1
GRCH37_POS_RE = re.compile(f"https://www.ncbi.nlm.nih.gov/variation/view/[?]chr=(?P<chr>[0-9]+)(&|&amp;)q=(&|&amp;)assm=GCF_000001405.25(&|&amp;)from=(?P<from>[0-9]+)(&|&amp;)to=(?P<to>[0-9]+)", re.IGNORECASE)

CLINVAR_NOT_FOUND_RS_RE = re.compile(f"has not been reported to ClinVar. Refer to dbSNP record {RS_RE.pattern} for details on variation at this location", re.IGNORECASE)

SUMMARY_TABLE_TEMPLATE = """
<table class='table'>
{% for summ, count in summary.items() %}
    <tr>
        <td>{{ summ }}</td>
        <td>{{ count }}</td>
    </tr>
{% endfor %}
</table>
"""

class Clinvar(Source):
    def set_entries(self):
        self.entries = {
            ("transcript", "pos"): self.transcript_cdot,
            ("chr", "pos", "ref", "alt"): self.chr_pos_ref_alt,
            #("chr", "pos"): self.chr_pos,
        }

    def parse_clinvar_html(self, clinvar_text) -> dict:
        result = {}

        not_found_rs_match = CLINVAR_NOT_FOUND_RS_RE.search(clinvar_text)
        if not_found_rs_match:
            result.update(**not_found_rs_match.groupdict())
            self.log_warning("Not found in Clinvar")
            return result

        header_match = HEADER_RE.search(clinvar_text)
        if header_match:
            result.update(**header_match.groupdict())
            result["cdot"] = html.unescape(result["cdot"])

        rs_match = RS_URL_RE.search(clinvar_text)
        if rs_match:
            result["rs"] =  rs_match.group("rs")
            result["rs_url"] =  rs_match.group(0)
        
        clingen_match = CLINGEN_RE.search(clinvar_text)
        if clingen_match:
            result["clingen_id"] =  clingen_match.group("id")
            result["clingen_url"] =  clingen_match.group(0)

        pos_grch37_match = GRCH37_POS_RE.search(clinvar_text)
        if pos_grch37_match:
            result.update(**pos_grch37_match.groupdict())

        if "to" in result:
            result["pos"] = result["to"]

        return result

    def get_summary_table(self, clinvar_text):
        soup = BeautifulSoup(clinvar_text, "html.parser")

        clinical_sign_table = soup.find("div", {"id": "id_second"})
        if not clinical_sign_table:
            self.log_debug("No Clinical sign table")
            return ""
        clinical_sign_tbody = clinical_sign_table.find("tbody")

        card_text = ""
        summary_dict = defaultdict(int)
        for row in clinical_sign_tbody.find_all("tr"):
            cols = row.find_all("td")
            condition, interpretation, submissions, status, last, variation = [e.text.strip() for e in cols]
            summary_dict[interpretation] += 1

        template = Environment(loader=BaseLoader).from_string(SUMMARY_TABLE_TEMPLATE)
        return template.render(summary=summary_dict)


    async def process(self, url):
        if "rs" in self.variant:
            rs = self.variant["rs"]
            clinvar_miner_url = f"https://clinvarminer.genetics.utah.edu/search?q={rs}"
            self.html_links["miner"] = SourceURL("miner", clinvar_miner_url)
            self.complete = True
        else:
            self.complete = False

        response, clinvar_text = await self.async_get_text(url)

        if "main" in self.html_links:
            if "/clinvar/variation/" not in self.html_links["main"].url:
                self.html_links["main"].url = str(response.url)
            else:
                self.complete = True
        else:
            self.html_links["main"] = SourceURL("Go", str(response.url))

        self.html_text = self.get_summary_table(clinvar_text)

        if not self.html_text:  # No summary table means not found?
            self.found = False

        self.new_variant_data.update(self.parse_clinvar_html(clinvar_text))
    
    async def transcript_cdot(self):
        transcript = self.variant["transcript"]
        cdot = self.variant["cdot"]

        transcript_cdot = f"{transcript}:{cdot}"

        url = f"https://www.ncbi.nlm.nih.gov/clinvar/?term={transcript_cdot}"
        await self.process(url)


    async def chr_pos_ref_alt(self):
        chrom = self.variant["chr"]
        pos = self.variant["pos"]
        ref = self.variant["ref"]
        alt = self.variant["alt"]
        url = f"https://www.ncbi.nlm.nih.gov/clinvar/?term={chrom}[CHR]+AND+{pos}[chrpos37]+{ref}>{alt}"
        await self.process(url)

    async def chr_pos(self):
        chrom = self.variant["chr"]
        pos = self.variant["pos"]
        url = f"https://www.ncbi.nlm.nih.gov/clinvar/?term={chrom}[CHR]+AND+{pos}[chrpos37]"
        await self.process(url)
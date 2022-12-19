from jinja2 import Environment, BaseLoader
from pydantic import BaseSettings, Field

from .source_result import Source, SourceURL

TMPL = """
{% for diag_implic in diagnostic_implications %}
    <div class='text-sm' style="color:{{ diag_implic.tumorType.color }}">{{ diag_implic.tumorType.name }}</div>
{% endfor %}
"""

class Secrets(BaseSettings):
    api_key: str = Field(None, env="ONCOKB_API_KEY")

secrets = Secrets()
class OncoKB(Source):
    def set_entries(self):
        self.entries = {
            ("gene", ): self.gene,
            ("gene", "pdot"): self.gene_pdot,
            ("chr", "pos", "alt", "ref"): self.chr_pos_alt_ref,
        }

    async def gene(self):
        gene = self.variant["gene"]
        url = f"https://www.oncokb.org/gene/{gene}"

        self.html_links["gene"] = SourceURL("Gene", url)

    async def gene_pdot(self):
        gene = self.variant["gene"]
        pdot = self.variant["pdot"]
        pdot_short = str(pdot).replace("p.", "").capitalize()

        # url = f"https://www.oncokb.org/api/private/search/variants/biological?hugoSymbol={gene}"
        url = f"https://www.oncokb.org/api/private/utils/variantAnnotation?hugoSymbol={gene}&referenceGenome=GRCh37&alteration={pdot_short}"

        auth_header = {"Authorization": f"Bearer {secrets.api_key}"}
        resp, response_json = await self.async_get_json(url, headers=auth_header)

        if "title" in response_json:
            title = response_json["title"]
            if title == "Unauthorized":
                self.html_text = "API key expired"
                self.complete = True
                self.found = False
                return

        oncogenic = response_json["oncogenic"]
        if "Unknown" in oncogenic:
            oncogenic = "Unknown/Not Found"

        self.html_text = oncogenic

        self.html_links["gene_pdot"] = SourceURL("Variant", f"https://www.oncokb.org/gene/{gene}/{pdot_short}")

        self.complete = True

    async def chr_pos_alt_ref(self):
        chrom = self.variant["chr"]
        pos = self.variant["pos"]
        ref = self.variant["ref"]
        alt = self.variant["alt"]

        url = f"https://www.oncokb.org/api/v1/annotate/mutations/byGenomicChange?genomicLocation={chrom},{pos},{pos},{ref},{alt}&referenceGenome=GRCh37"
        auth_header = {"Authorization": f"Bearer {secrets.api_key}"}
        resp, response_json = await self.async_get_json(url, headers=auth_header)

        if "title" in response_json:
            title = response_json["title"]
            if title == "Unauthorized":
                self.html_text = "API key expired"
                self.complete = True
                self.found = False
                return

        if "query" in response_json:
            query = response_json["query"]

            if "hugoSymbol" in query:
                gene = query["hugoSymbol"]
                if gene:
                    self.new_variant_data["gene"] = gene
                    url = f"https://www.oncokb.org/gene/{query['hugoSymbol']}"
                    self.html_links["main"] = SourceURL("Go", url)

            if "alteration" in query:
                pdot = query["alteration"]
                if pdot:
                    self.new_variant_data["pdot"] = f'p.{pdot}'
            
            if "proteinStart" in query:
                self.new_variant_data["p_start"] = query["proteinStart"]

            if "proteinEnd" in query:
                self.new_variant_data["p_end"] = query["proteinEnd"]

            if "hgvs" in query:
                self.new_variant_data["hgvs_id"] = query["hgvs"]

        template = Environment(loader=BaseLoader).from_string(TMPL)
        if "diagnosticImplications" in response_json:
            diagnosticImplications = response_json["diagnosticImplications"]

            self.html_text = template.render(diagnostic_implications=diagnosticImplications)

        # self.complete = True


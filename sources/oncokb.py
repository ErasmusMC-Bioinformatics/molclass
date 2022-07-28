from jinja2 import Environment, BaseLoader

from .source_result import Source, SourceURL

TMPL = """
{% for diag_implic in diagnostic_implications %}
    <div class='text-sm' style="color:{{ diag_implic.tumorType.color }}">{{ diag_implic.tumorType.name }}</div>
{% endfor %}
"""

class OncoKB(Source):
    def set_entries(self):
        self.entries = {
            ("gene", ): self.gene,
            ("chr", "pos", "alt", "ref"): self.chr_pos_alt_ref,
        }

    async def gene(self):
        gene = self.variant["gene"]
        url = f"https://www.oncokb.org/gene/{gene}"

        self.html_links["main"] = SourceURL("Go", url)

    async def chr_pos_alt_ref(self):
        chrom = self.variant["chr"]
        pos = self.variant["pos"]
        ref = self.variant["ref"]
        alt = self.variant["alt"]

        url = f"https://demo.oncokb.org:443/api/v1/annotate/mutations/byGenomicChange?genomicLocation={chrom},{pos},{pos},{ref},{alt}&referenceGenome=GRCh37"
        print(url)
        resp, response_json = await self.async_get_json(url)

        if "query" in response_json:
            query = response_json["query"]

            if "hugoSymbol" in query:
                gene = query["hugoSymbol"]
                if gene:
                    self.new_variant_data["gene"] = gene
                    url = f"https://www.oncokb.org/gene/{query['hugoSymbol']}"
                    self.html_links["main"] = SourceURL("Go", url)
            
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

        self.complete = True


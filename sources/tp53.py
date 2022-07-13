from .source_result import Source

class TP53(Source):
    def set_entries(self):
        self.entries = {
            ("gene", "cdot"): self.gene_cdot,
        }

    async def gene_cdot(self):
        gene = self.variant["gene"]
        if gene != "TP53":
            self.complete = True
            self.executed = True
            return

        cdot = self.variant["cdot"]

        url = f"https://tp53.isb-cgc.org/results_somatic_mutation_list"

        text = f"""
        <form target="_blank" action="{url}" method="post">
            <input name="sm_include_cdna_list" value="{cdot}" type="hidden" />
            <input type="submit" value="Go"  class="btn btn-primary">
        </input>"""

        self.set_html(text=text)
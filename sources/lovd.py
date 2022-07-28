from html import escape
from lxml import etree
from .source_result import Source, SourceURL

class LOVD(Source):
    def set_entries(self):
        self.entries = {
            ("gene", ): self.gene,
            ("gene", "cdot"): self.gene_cdot,
        }

    async def gene(self):
        gene = self.variant["gene"]
        url = f"https://databases.lovd.nl/shared/variants/{gene}/unique"

        self.html_links["main"] = SourceURL("Gene", url)

    async def gene_cdot(self):
        gene = self.variant["gene"]
        url = f"https://databases.lovd.nl/shared/variants/{gene}/unique"
        self.html_links["main"] = SourceURL("Gene", url)
        
        cdot = self.variant["cdot"]

        resp, lovd_text = await self.async_get_text(url)
        tree = etree.HTML(bytes(lovd_text, encoding='utf8'))
        transcript_id_input = tree.xpath("//input[@name='search_transcriptid']")
        if not transcript_id_input:
            self.log_warning("Could not extract transcript_id from lovd page")
            return
        
        transcript_id_input = transcript_id_input[0]
        transcript_id = transcript_id_input.get("value")

        encoded_cdot = escape(cdot)
        variant_url = f"https://databases.lovd.nl/shared/variants/{gene}?search_vot_clean_dna_change={encoded_cdot}&search_transcriptid={transcript_id}&page_size=1000"

        resp, variant_page = await self.async_get_text(variant_url)
        any_rows_on_page = variant_page.count("data-href")
        if any_rows_on_page < 0:
            self.log_warning(f"No rows found for '{cdot}'")
            self.html_text = "Variant not found"
        else:
            self.html_links["variant"] = SourceURL("Variant", variant_url)

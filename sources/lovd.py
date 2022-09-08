from collections import defaultdict
from html import escape
import re
from bs4 import BeautifulSoup
from jinja2 import BaseLoader, Environment
from lxml import etree

from .source_result import Source, SourceURL

SUMMARY_TABLE_TEMPLATE = """
<table class='table caption-top'>
    <caption>{{ entries }} entries - {{ vkgl_entries }} VKGL-NL</caption>
{% for summ, count in vkgl_summary.items() %}
    <tr>
        <td>{{ summ }}</td>
        <td>{{ count }}</td>
    </tr>
{% endfor %}
</table>

{% if insight_summary %}
    <table class='table caption-top'>
        <caption>{{ insight_entries }} InSiGHT</caption>
    {% for summ, count in insight_summary.items() %}
        <tr>
            <td>{{ summ }}</td>
            <td>{{ count }}</td>
        </tr>
    {% endfor %}
    </table>
{% endif %}
"""
class LOVD(Source):
    def set_entries(self):
        self.entries = {
            ("gene", ): self.gene,
            ("gene", "cdot"): self.gene_cdot,
        }

    async def gene(self):
        gene = self.variant["gene"]
        url = f"https://databases.lovd.nl/shared/variants/{gene}/unique"
        self.found = False

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
            self.found = False
            return

        
        transcript_id_input = transcript_id_input[0]
        transcript_id = transcript_id_input.get("value")
        
        self.log_debug(f"Got transcript_id {transcript_id}")

        encoded_cdot = cdot
        variant_url = f"https://databases.lovd.nl/shared/variants/{gene}?search_vot_clean_dna_change={encoded_cdot}&search_transcriptid={transcript_id}&page_size=1000"
        resp, variant_page = await self.async_get_text(variant_url)
        any_rows_on_page = variant_page.count("data-href")
        if any_rows_on_page <= 0:
            self.log_warning(f"No rows found for '{cdot}'")
            self.found = False
            self.html_text = "Variant not found"
            return

        self.html_links["variant"] = SourceURL("Variant", variant_url)
        
        soup = BeautifulSoup(variant_page, "html.parser")

        entry_table = soup.find(id=re.compile("viewlistTable_CustomVL.*"))
        if not entry_table:
            self.log_warning("No entry table found")
            self.html_text = "Variant table not found"
            return

        table_header = [e.text.strip() for e in entry_table.findAll("th")]
        classification_index = table_header.index("Clinical\xa0classification")
        owner_index = table_header.index("Owner")

        vkgl_summary_dict = defaultdict(int)
        insight_dict = defaultdict(int)
        row_count = 0
        for row in entry_table.findAll("tr", {"class": "data"}):
            cols = row.findAll("td")
            cols = [e.text.strip() for e in cols]
            try:
                classification = cols[classification_index]
                owner = cols[owner_index]
            except ValueError as e:
                self.log_warning(f"Could not index cols {classification_index} {owner_index}")
                continue
            row_count += 1
            if "VKGL-NL" in owner:
                vkgl_summary_dict[classification] += 1
            if "InSiGHT" in owner:
                insight_dict[classification] += 1
        
        if gene not in ["MLH1", "PMS2", "MSH2", "MSH6"]:
            insight_dict = {}

        template = Environment(loader=BaseLoader).from_string(SUMMARY_TABLE_TEMPLATE)
        self.html_text = template.render(
            vkgl_summary=vkgl_summary_dict, 
            vkgl_entries=sum(vkgl_summary_dict.values()),
            insight_summary=insight_dict,
            insight_entries=sum(insight_dict.values()),
            entries=row_count
        )

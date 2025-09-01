from collections import defaultdict
from html import escape
import re
import urllib.parse
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
            ("gene", "gene_cdot"): self.gene_cdot,
            ("gene", "cdot"): self.gene_cdot,
        }

    async def gene(self):
        gene = self.variant["gene"]
        url = f"https://databases.lovd.nl/shared/variants/{gene}/unique"
        self.found = False

        self.html_links["main"] = SourceURL("Gene", url)

    async def gene_cdot(self):
        """
        Searches the LOVD website for a variant, then performs a secondary request and 
        parses the variant page, if it exists
        """
        gene = self.variant["gene"]
        cdot = self.variant["gene_cdot"]
        enc_gene = urllib.parse.quote(gene)
        enc_cdot = urllib.parse.quote(cdot)
        query_url = f"https://databases.lovd.nl/shared/api/rest.php/variants/{enc_gene}?search_position={enc_cdot}&show_variant_effect=1&format=application/json"
        resp, json = await self.async_get_json(query_url)

        transcript = json[0]["position_mRNA"][0].split(":")[0]

        url = f"https://databases.lovd.nl/shared/variants/{enc_gene}/unique"
        variant_url = f"https://databases.lovd.nl/shared/transcripts/{transcript}"

        self.html_links["main"] = SourceURL("Gene", url)
        self.html_links["variant"] = SourceURL("Transcript", variant_url)

        vkgl_summary_dict = defaultdict(int)
        insight_dict = defaultdict(int)
        row_count = 0

        for gene_object in json:
            if "VKGL-NL" in gene_object["owned_by"][0]:
                vkgl_summary_dict[gene_object["effect_reported"][0]] += 1
            if "InSiGHT" in gene_object["owned_by"][0]:
                insight_dict[gene_object["effect_reported"][0]] += 1
            row_count += 1

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

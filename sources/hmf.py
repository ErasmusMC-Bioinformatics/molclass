import aiofiles

from jinja2 import Environment, BaseLoader

from .source_result import Source, SourceURL

SUMMARY_TABLE_TEMPLATE = """
<table class='table caption-top'>
    <caption>Sources</caption>
{% for source in sources %}
    <tr>
        <td>{{ source }}</td>
    </tr>
{% endfor %}
</table>
"""

class HMF(Source):
    def set_entries(self):
        self.entries = {
            ("chr", "pos", "ref", "alt"): self.chr_pos_ref_alt,
        }

    async def chr_pos_ref_alt(self):
        chrom = self.variant["chr"]
        pos = self.variant["pos"]
        ref = self.variant["ref"]
        alt = self.variant["alt"]
        if info := await self.lookup_variant(chrom, pos, ref, alt):
            gene = info[0]
            ensembl = info[1]
            pdot = info[2]
            sources = info[3].split(",")
            
            self.new_variant_data["gene"] = gene
            self.new_variant_data["ensembl_transcript"] = ensembl
            self.new_variant_data["pdot"] = pdot

            template = Environment(loader=BaseLoader).from_string(SUMMARY_TABLE_TEMPLATE)
            self.html_text = template.render(sources=sources)
        else:
            self.found = False

    
    async def lookup_variant(self, chrom, pos, ref, alt):
        async with aiofiles.open('databases/hmf_hotspots.tsv', mode='r') as f:
            async for line in f:
                chrom_other, pos_other, ref_other, alt_other, gene, ensembl, pdot, sources = line.split("\t")
                if (chrom, pos, ref, alt) == (chrom_other, pos_other, ref_other, alt_other):
                    return (gene, ensembl, pdot, sources.strip())

    def get_name(self):
        return "HMF Hotspots"
import os

import aiofiles

from jinja2 import Environment, BaseLoader

from util import reverse_complement
from pydantic import BaseSettings, Field
from .source_result import Source, SourceURL

SUMMARY_TABLE_TEMPLATE = """
<table class='table caption-top fs-6'>
    <caption>Sources</caption>
    <tr>
        <td>DoCM (<a href="http://www.docm.info/">http://www.docm.info/</a>)</td>
        <td class='table-{{ 'success' if "docm" in sources else 'danger' }}'>{{ 'Yes' if "docm" in sources else 'No' }}</td>
    </tr>
    <tr>
        <td>CIVIC (<a href="https://civicdb.org/">https://civicdb.org/</a>)</td>
        <td class='table-{{ 'success' if "vicc_civic" in sources else 'danger' }}'>{{ 'Yes' if "vicc_civic" in sources else 'No' }}</td>
    </tr>
    <tr>
        <td>CGI (Cancer Genome Interpreter)</td>
        <td class='table-{{ 'success' if "vicc_cgi" in sources else 'danger' }}'>{{ 'Yes' if "vicc_cgi" in sources else 'No' }}</td>
    </tr>
    <tr>
        <td>HMF WGS cohort</td>
        <td class='table-{{ 'success' if "hartwig_cohort" in sources else 'danger' }}'>{{ 'Yes' if "hartwig_cohort" in sources else 'No' }}</td>
    </tr>
</table>
"""

class Secrets(BaseSettings):
    hmf_database: str = Field("databases/hmf_hotspots.tsv", env="HMF_DATABASE")

secrets = Secrets()
class HMF(Source):
    def set_entries(self):
        self.entries = {
            ("chr", "pos", "ref", "alt"): self.chr_pos_ref_alt,
        }

    def is_complete(self) -> bool:
        if not os.path.exists(secrets.hmf_database):
            print("Could not find HMF hotspot database:", secrets.hmf_database)
            return False
        return True

    async def chr_pos_ref_alt(self):
        chrom = self.variant["chr"]
        pos = self.variant["pos"]
        ref = self.variant["ref"]
        alt = self.variant["alt"]
        sources = set()
        template = Environment(loader=BaseLoader).from_string(SUMMARY_TABLE_TEMPLATE)
        if info := await self.lookup_variant(chrom, pos, ref, alt):
            gene = info[0]
            ensembl = info[1]
            pdot = info[2]
            sources = set(info[3].split(","))
            
            if gene != "null":
                self.new_variant_data["gene"] = gene
            if ensembl != "null":
                self.new_variant_data["ensembl_transcript"] = ensembl
            self.new_variant_data["pdot"] = pdot

        self.html_text = template.render(sources=sources)
    
    async def lookup_variant(self, chrom, pos, ref, alt):
        chrom = str(chrom)
        pos = str(pos)
        async with aiofiles.open('databases/hmf_hotspots.tsv', mode='r') as f:
            async for line in f:
                chrom_other, pos_other, ref_other, alt_other, gene, ensembl, pdot, sources = line.split("\t")
                if (chrom, pos) != (chrom_other, pos_other):
                    continue

                if (ref, alt) == (ref_other, alt_other) or (ref and alt and reverse_complement(ref), reverse_complement(alt)) == (ref_other, alt_other):
                    return (gene, ensembl, pdot, sources.strip())

    def get_name(self):
        return "HMF Hotspots Database"
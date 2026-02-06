import urllib.parse

from util import reverse_complement
from .source_result import Source, SourceURL

class GenomeNexus(Source):
    def set_entries(self):
        self.entries = {
            ("transcript", "cdot", "chr"): self.transcript_cdot,
            ("chr", "pos", "ref", "alt"): self.chr_pos_ref_alt
        }

    async def check_validity(self, query):
        enc_query = urllib.parse.quote(query)
        api_url = f"https://www.genomenexus.org/annotation/{enc_query}?fields=annotation_summary"
        resp, json = await self.async_get_json(api_url)
        return json.get("successfully_annotated", False)

    async def chr_pos_ref_alt(self):
        """
        Simply add a URL to the variant, won't work for more del, ins, dup, etc.
        Probably could add support for those, but would take other fields then pos, ref, alt.
        """
        chrom = self.variant["chr"]
        pos = self.variant["pos"]
        ref = self.variant["ref"]
        alt = self.variant["alt"]

        # Check if annotation exists for ref/alt, if not try the reverse complement
        if not await self.check_validity(f"{chrom}:g.{pos}{ref}>{alt}"):
            ref = reverse_complement(ref)
            alt = reverse_complement(alt)
            if not await self.check_validity(f"{chrom}:g.{pos}{ref}>{alt}"):
                self.html_text = (f"No annotation found for either {chrom}:g.{pos}{self.variant['ref']}>{self.variant['alt']} "
                                  f"or {chrom}:g.{pos}{ref}>{alt} (reverse complement).")
                self.found = False
                return

        url = f"https://www.genomenexus.org/variant/{chrom}:g.{pos}{ref}>{alt}"
        self.html_links["main"] = SourceURL(f"{chrom}:g.{pos}{ref}>{alt}", url)

    async def transcript_cdot(self):
        """
        Use mutalyzer to retrieve genomic position
        """
        transcript = self.variant["transcript"]
        cdot = self.variant["cdot"]
        chrom = self.variant["chr"]

        enc_query = urllib.parse.quote(f"{transcript}:{cdot}")
        api_url = f"https://mutalyzer.nl/api/map/?description={enc_query}&reference_id=GRCH37&filter_out=true"
        resp, json = await self.async_get_json(api_url)
        genomic_desc = json.get("genomic_description", False)
        if not genomic_desc:
            self.found = False
            return
        
        _, gdot = genomic_desc.split(":")
        url = f"https://www.genomenexus.org/variant/{chrom}:{gdot}"
        self.html_links["main"] = SourceURL(f"{chrom}:{gdot}", url)
        self.complete = True

    def get_name(self):
        return "Genome Nexus"
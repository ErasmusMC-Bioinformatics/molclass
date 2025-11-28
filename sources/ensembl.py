import re

from .source_result import Source

HEADER_GENE_RE = re.compile(r"\((?!p\.)(?P<gene>[^\)]+)", re.IGNORECASE)
JSOND_RE = re.compile('href="(?P<url>/allele/[^"]+)"')

class Ensembl(Source):
    def set_entries(self):
        self.entries = {
            ("rs",): self.rs,
        }

    def is_hidden(self) -> bool:
        """
        Ensemble Source is just used for consensus, so no need to show it
        """
        return True

    async def rs(self):
        """
        Queries the ensembl API with the rs# and adds a bunch of meta data
        """
        rs = self.variant['rs']

        url = f"https://grch37.rest.ensembl.org/vep/human/id/{rs}"

        resp, ensembl_result = await self.async_get_json(url, headers={'Content-Type': 'application/json'})
        
        if resp.status != 200:
            return

        try:
            ensembl_result = ensembl_result[0]
        except Exception:
            self.log_warning("Empty response")
            return
            
        if "transcript_consequences" not in ensembl_result:
            self.log_warning("No 'transcript_consequences' in response")
            return

        gene = ""
        rs = ""
        pdot_from = ""
        pdot_to = ""
        pdot_pos = None
        for cons in ensembl_result["transcript_consequences"]:
            if not gene:
                gene = cons.get("gene_symbol", None)

            if not rs:
                rs = cons.get("id", None)

            if not (pdot_from or pdot_to):
                try:
                    aa = cons["amino_acids"]
                    pdot_from, pdot_to = aa.split("/")
                except Exception:
                    pass
            
            if not pdot_pos:
                pdot_pos = cons.get("protein_end", None)

        
        if gene:
            self.new_variant_data["gene"] = gene
        
        if rs:
            self.new_variant_data["rs"] = rs

        if pdot_from:
            self.new_variant_data["pdot_from"] = pdot_from

        if pdot_to:
            self.new_variant_data["pdot_to"] = pdot_to

        if pdot_pos:
            self.new_variant_data["pdot_pos"] = pdot_pos
            
        self.complete = True

        
        
        

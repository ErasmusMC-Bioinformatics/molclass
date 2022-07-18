from .source_result import Source, SourceURL

class Alamut(Source):
    def set_entries(self):
        self.entries = {
            ("rs", ): self.everything,
            ("transcript",): self.everything,
        }

    async def everything(self):
        variant_set = set(self.variant)
        if set(["chr", "pos"]).issubset(variant_set):
            chrom = self.variant["chr"]
            pos = self.variant["pos"]
            url = f"http://127.0.0.1:10000/search?institution=ANL0016&apikey=18565976&request=chr{chrom}:{pos}"
            self.html_links["position"] = SourceURL("Position", url)

        if "rs" in self.variant:
            db_snp_url = f"http://127.0.0.1:10000/search?institution=ANL0016&apikey=18565976&request={self.variant['rs']}"
            self.html_links["rs"] = SourceURL("rs", db_snp_url)

        if "gene" in self.variant:
            gene = self.variant["gene"]
            if "transcript" in self.variant:
                transcript = self.variant["transcript"]
                gene_url = f"http://127.0.0.1:10000/search?institution=ANL0016&apikey=18565976&request={gene} {transcript}"
            else:
                gene_url = f"http://127.0.0.1:10000/search?institution=ANL0016&apikey=18565976&request={gene}"
            self.html_links["gene"] = SourceURL("Gene", gene_url)
        
        if "transcript" in self.variant and "cdot" in self.variant:
            transcript = self.variant["transcript"]
            cdot = self.variant["cdot"]
            transcript_cdot = f"{transcript}:{cdot}"
            url = f"http://127.0.0.1:10000/search?institution=ANL0016&apikey=18565976&request={transcript_cdot}"
            
            self.html_links["transcript:cdot"] = SourceURL("Transcript:cdot", url)
                    
        if len(self.html_links) == 4:
            self.complete = True
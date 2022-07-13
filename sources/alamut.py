from .source_result import Source

class Alamut(Source):
    def set_entries(self):
        self.entries = {
            ("rs", ): self.everything,
            ("transcript",): self.everything,
        }

    async def everything(self):
        urls = []
        variant_set = set(self.variant)
        if set(["chr", "pos"]).issubset(variant_set):
            chrom = self.variant["chr"]
            pos = self.variant["pos"]
            url = f"http://127.0.0.1:10000/search?institution=ANL0016&apikey=18565976&request=chr{chrom}:{pos}"
            urls.append({"url": url, "text": "Pos"})

        if "rs" in self.variant:
            db_snp_url = f"http://127.0.0.1:10000/search?institution=ANL0016&apikey=18565976&request={self.variant['rs']}"
            urls.append({
                "url": db_snp_url, "text": "rs#"
            })

        if "gene" in self.variant:
            gene = self.variant["gene"]
            if "transcript" in self.variant:
                transcript = self.variant["transcript"]
                gene_url = f"http://127.0.0.1:10000/search?institution=ANL0016&apikey=18565976&request={gene} {transcript}"
            else:
                gene_url = f"http://127.0.0.1:10000/search?institution=ANL0016&apikey=18565976&request={gene}"
            urls.append({
                "url": gene_url, "text": "Gene"
            })
        
        if "transcript" in self.variant and "cdot" in self.variant:
            transcript = self.variant["transcript"]
            cdot = self.variant["cdot"]
            url = f"http://127.0.0.1:10000/search?institution=ANL0016&apikey=18565976&request={transcript}:{cdot}"
            urls.append({
                "url": url, "text": "Transcript:cdot"
            })
        
        if len(urls) == 4:
            self.complete = True
        
        self.set_html(links=urls)

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
            transcript_cdot = f"{transcript}:{cdot}"
            url = f"http://127.0.0.1:10000/search?institution=ANL0016&apikey=18565976&request={transcript_cdot}"
            urls.append({
                "url": url, "text": "Transcript:cdot"
            })
            """
            print(f"http://127.0.0.1:10000/annotate?institution=ANL0016&apikey=18565976&variant={transcript_cdot}")
            alamut = await self.async_get_json(f"http://127.0.0.1:10000/annotate?institution=ANL0016&apikey=18565976&variant={transcript_cdot}")
            
            self.new_variant_data["alamut_classification"] = alamut["Classification"]
            self.new_variant_data["clinvar_id"] = alamut["Clinvar Id"]
            self.new_variant_data["cosmic_id"] = alamut["Cosmic Id"]
            self.new_variant_data["cosmic_id"] = alamut["Cosmic Id"]
            self.new_variant_data["gene"] = alamut["Gene"]
            self.new_variant_data["hgnc_gene_id"] = alamut["HGNC Gene Id"]
            self.new_variant_data["hpo_id"] = alamut["HPO Id (from Clinvar)"]
            self.new_variant_data["medgen_id"] = alamut["Medgen Id (from Clinvar)"]
            self.new_variant_data["mondo_id"] = alamut["Mondo Id (from Clinvar)"]
            self.new_variant_data["omim_id"] = alamut["OMIM Id (from Clinvar)"]
            self.new_variant_data["orphanet_id"] = alamut["Orphanet Id (from Clinvar)"]
            self.new_variant_data["uniprot_id"] = alamut["Uniprot Id"]
            self.new_variant_data["rs"] = alamut["dbSNP rsId"]
            """

        
        if len(urls) == 4:
            self.complete = True
        
        self.set_html(links=urls)

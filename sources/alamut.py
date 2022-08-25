from pydantic import BaseSettings, Field

from .source_result import Source, SourceURL

# 10.92.3.212
class Secrets(BaseSettings):
    ip: str = Field(None, env="ALAMUT_IP")
    institution: str = Field(None, env="ALAMUT_INSTITUTION")
    api_key: str = Field(None, env="ALAMUT_API_KEY")

secrets = Secrets()

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
            url = f"http://127.0.0.1:10000/search?institution={secrets.institution}&apikey={secrets.api_key}&request=chr{chrom}:{pos}"
            self.html_links["position"] = SourceURL("Position", url)

        if "rs" in self.variant:
            db_snp_url = f"http://127.0.0.1:10000/search?institution={secrets.institution}&apikey={secrets.api_key}&request={self.variant['rs']}"
            self.html_links["rs"] = SourceURL("rs", db_snp_url)

        if "gene" in self.variant:
            gene = self.variant["gene"]
            if "transcript" in self.variant:
                transcript = self.variant["transcript"]
                gene_url = f"http://127.0.0.1:10000/search?institution={secrets.institution}&apikey={secrets.api_key}&request={gene} {transcript}"
            else:
                gene_url = f"http://127.0.0.1:10000/search?institution={secrets.institution}&apikey={secrets.api_key}&request={gene}"
            self.html_links["gene"] = SourceURL("Gene", gene_url)
        
        if "transcript" in self.variant and "cdot" in self.variant:
            transcript = self.variant["transcript"]
            cdot = self.variant["cdot"]
            transcript_cdot = f"{transcript}:{cdot}"
            url = f"http://127.0.0.1:10000/search?institution={secrets.institution}&apikey={secrets.api_key}&request={transcript_cdot}"
            
            self.html_links["transcript:cdot"] = SourceURL("Transcript:cdot", url)

            if secrets.ip:
                await self.get_and_parse_annotate()
                    
        if len(self.html_links) == 4:
            self.complete = True

    async def get_and_parse_annotate(self):
        transcript = self.variant["transcript"]
        cdot = self.variant["cdot"]
        transcript_cdot = f"{transcript}:{cdot}"
        url = f"http://{secrets.ip}/annotate?institution={secrets.institution}&apikey={secrets.api_key}&variant={transcript_cdot}"

        resp, alamut = await self.async_get_json(url)

        if resp.status != 200:
            self.html_text = "Can't connect to Alamut PC"
            self.log_error("Can't connect to Alamut PC")
            return

        self.new_variant_data["chr"] = alamut["Chromosome"]
        self.new_variant_data["pos"] = alamut["gDNA end"]
        self.new_variant_data["start"] = alamut["gDNA start"]
        self.new_variant_data["end"] = alamut["gDNA end"]
        self.new_variant_data["ref"] = alamut["Substitution: wild-type nucleotide"]
        self.new_variant_data["alt"] = alamut["Substitution: variant nucleotide"]
        self.new_variant_data["cdot"] = alamut["cNomen"]
        self.new_variant_data["transcript"] = alamut["Transcript"]
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


        

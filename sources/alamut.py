from typing import Tuple
from pydantic import BaseSettings, Field

from aiohttp.client_exceptions import ClientConnectorError, ContentTypeError

from util import get_pdot_abbreviation, reverse_complement

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
            ("transcript", "transcript_version"): self.everything,
        }

    def is_complete(self) -> bool:
        if not secrets.ip:
            print("Need ALAMUT_IP env variable for Alamut source")        
            return False
        if not secrets.institution:
            print("Need ALAMUT_INSTITUTION env variable for Alamut source")        
            return False
        if not secrets.api_key:
            print("Need ALAMUT_API_KEY env variable for Alamut source")        
            return False
        return True

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
            _, transcript = self.get_transcript_with_version(self.variant["transcript"])
            cdot = self.variant["cdot"]

            transcript_cdot = f"{transcript}:{cdot}"
            url = f"http://127.0.0.1:10000/search?institution={secrets.institution}&apikey={secrets.api_key}&request={transcript_cdot}"
            
            self.html_links["transcript:cdot"] = SourceURL("Transcript:cdot", url)

            if secrets.ip:
                 if not await self.get_and_parse_annotate():
                    return
        

                    
        if len(self.html_links) == 4:
            self.complete = True

    def get_transcript_with_version(self, transcript) -> Tuple[bool, str]:  # returned with version, transcript
        # if searching without transcript version, version is always 'None', so grab it from consensus
        if self.variant["transcript_version"] is not None:
            return True, transcript  # already have version transcript
        
        versions = self.consensus["transcript_version"]
        if len(versions) == 1:
            return False, transcript  # no alternatives

        transcript_version = max(versions, key=lambda x: len(versions[x]) if x != "search" else -1)
        if transcript.endswith(transcript_version):
            return True, transcript  # just to be sure, dont want xxx.4.4

        return True, f"{transcript}{transcript_version}"

    async def get_and_parse_annotate(self) -> bool:
        transcript = self.variant["transcript"]
        with_version, transcript_v = self.get_transcript_with_version(transcript)
        if not with_version:
            return False

        if transcript != transcript_v:
            transcript = transcript_v
            warning_str = f"Result for {transcript}"
            self.matches_consensus = False
            if warning_str not in self.matches_consensus_tooltip:   
                self.matches_consensus_tooltip.append(warning_str)

        cdot = self.variant["cdot"]

        transcript_cdot = f"{transcript}:{cdot}"

        url = f"http://{secrets.ip}/annotate?institution={secrets.institution}&apikey={secrets.api_key}&variant={transcript_cdot}"

        # If the Alamut server isn't running nginx will just give an error page
        # which can't be parsed to json
        try:
            resp, alamut = await self.async_get_json(url)
        except (ClientConnectorError, ContentTypeError) as e:
            alamut_maybe_down_str = "Alamut might be down?"
            self.matches_consensus = False
            if alamut_maybe_down_str not in self.matches_consensus_tooltip:
                self.matches_consensus_tooltip.append(alamut_maybe_down_str)
            return True

        if resp.status != 200:
            self.html_text = "Can't connect to Alamut PC"
            self.log_error("Can't connect to Alamut PC")
            return True

        self.new_variant_data["chr"] = alamut["Chromosome"]
        self.new_variant_data["pos"] = alamut["gDNA end"]
        self.new_variant_data["start"] = alamut["gDNA start"]
        self.new_variant_data["end"] = alamut["gDNA end"]
        self.new_variant_data["ref"] = alamut["Substitution: wild-type nucleotide"]
        self.new_variant_data["alt"] = alamut["Substitution: variant nucleotide"]

        if alamut.get("Strand", None) == "-1":  # fix reverse complement ref/alt for -1 'strandedness'
            self.new_variant_data["ref"] = reverse_complement(self.new_variant_data["ref"])
            self.new_variant_data["alt"] = reverse_complement(self.new_variant_data["alt"])

        self.new_variant_data["cdot"] = alamut["cNomen"]
        self.new_variant_data["pdot"] = get_pdot_abbreviation(alamut["pNomen"].replace("(", "").replace(")", ""))
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

        thousand_genomes_freq_all = alamut["1000 Genomes Freq. All"]
        if thousand_genomes_freq_all == "":
            thousand_genomes_freq_all = "N/A"
        self.new_variant_data["1000_genomes_freq_all"] = thousand_genomes_freq_all

        esp_freq_all = alamut["ESP Alt. Allele Freq. All"]
        if esp_freq_all == "":
            esp_freq_all = "N/A"
        self.new_variant_data["esp_freq_all"] = esp_freq_all

        gnomad_freq_all = alamut["Gnomad Exome Freq. All"]
        if gnomad_freq_all == "":
            gnomad_freq_all = "N/A"
        self.new_variant_data["gnomad_freq_all"] = gnomad_freq_all

        gonl_allele_freq = alamut["GoNL Allele Freq."]
        if gonl_allele_freq == "":
            gonl_allele_freq = "N/A"
        self.new_variant_data["gonl_allele_freq"] = gonl_allele_freq

        distance_to_splice_site = alamut["Splicing (at junction): distance to splice site"]
        self.new_variant_data["distance_to_splice_site"] = distance_to_splice_site

        self.html_text = f"""
<table class='table'>
    <tr>
        <td>1000 Genomes Freq. All</td><td>{thousand_genomes_freq_all}</td>
    </tr>
    <tr>
        <td>ESP Alt. Allele Freq. All</td><td>{esp_freq_all}</td>
    </tr>
    <tr>
        <td>Gnomad Exome Freq. All</td><td>{gnomad_freq_all}</td>
    </tr>
    <tr>
        <td>GoNL Allele Freq.</td><td>{gonl_allele_freq}</td>
    </tr>
    <tr>
        <td>Distance to splice site</td><td>{distance_to_splice_site}</td>
    </tr>
</table>"""
        return True
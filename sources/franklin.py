from typing import Any
from search import parse_cdot, parse_pdot, parse_transcript
from util import get_pdot_abbreviation
from .source_result import Source, SourceURL



class Franklin(Source):
    def set_entries(self):
        self.entries = {
            ("rs",): self.rs,
            ("transcript", "cdot"): self.transcript_cdot,
            ("gene", "gene_cdot"): self.gene_cdot,
            ("chr", "pos", "ref", "alt"): self.chr_pos_ref_alt,
        }

    async def get_parse_search_response(self, search: str) -> tuple[Any, Any]:
        url = f"https://franklin.genoox.com/api/parse_search"

        post_data = {
            "reference_version": "hg19",
            "search_text_input": search
        }
        headers = {
            'Content-Type': "application/json",
            'Cache-Control': "no-cache",
        }

        response, resp = await self.async_post_json(url, json=post_data, headers=headers)
        return response, resp
    
    async def get_classification_response(self, chrom, pos, ref, alt) -> dict:
        url = f"https://franklin.genoox.com/api/classify"
        post_data = {
            "is_versioned_request":False,
            "variant":{
                "chrom":chrom,
                "pos": pos,
                "ref":ref,
                "alt":alt,
                "reference_version":"hg19"
            }
        }
        headers = {
            'Content-Type': "application/json",
            'Cache-Control': "no-cache",
        }
        async with self.session.post(url, json=post_data, headers=headers) as response:
            resp = await response.json()
            return resp

    def get_classification_color(self, classification):
        if classification == "Benign":
            return "6DFF6D"
        if classification == "LikelyBenign":
            return "4BAF4B"
        if classification == "VUS":
            return "FFA060"
        if classification == "LikelyPathogenic":
            return "FF6600"
        if classification == "Pathogenic":
            return "FF0000"
    
    async def process(self, response_json):
        if "best_variant_option" in response_json:
            variant = response_json["best_variant_option"]

            chrom = variant["chrom"].replace("chr", "")
            pos = variant["pos"]
            ref = variant["ref"]
            alt = variant["alt"]
            self.new_variant_data["pos"] = pos
            self.new_variant_data["chr"] = chrom

            """ # franklin seems to return the reverse complement, this is needed to get the variant detail below, but is 'wrong' for the rest
            self.new_variant_data["ref"] = ref
            self.new_variant_data["alt"] = alt
            """
            full_variant = variant["to_full_variant"]
            self.new_variant_data["start"] = full_variant["start"]
            self.new_variant_data["end"] = full_variant["end"]
            
            variant_detail_url = f"https://franklin.genoox.com/api/fetch_variant_details?chr=chr{chrom}&pos={pos}&ref={ref}&alt={alt}&reference_version=hg19"
            resp, franklin_variant_detail = await self.async_get_json(variant_detail_url)

            if "rs" in franklin_variant_detail:
                self.new_variant_data["rs"] = franklin_variant_detail["rs"]

            if "db_snp" in franklin_variant_detail:
                self.new_variant_data["rs"] = franklin_variant_detail["db_snp"]

            if "transcript" in franklin_variant_detail:
                self.new_variant_data["transcript"] = franklin_variant_detail["transcript"]

            if "gene" in franklin_variant_detail:
                self.new_variant_data["gene"] = franklin_variant_detail["gene"]

            classification_json = await self.get_classification_response(
                chrom, 
                pos, 
                ref, 
                alt
            )

            franklin_classification = classification_json.get("classification", "Unknown")
            if franklin_classification in ["ModeratePathogenicSupport", "LowPathogenicSupport"]:
                franklin_classification = "VUS"
            

            self.new_variant_data["franklin_classification"] = f"<p style='color: #{self.get_classification_color(franklin_classification)}'>{franklin_classification}</p>"

            
            if "gene" in classification_json:
                self.new_variant_data["gene"] = classification_json["gene"]
            if "c_dot" in classification_json:
                self.new_variant_data.update(parse_cdot(classification_json["c_dot"]))
                self.new_variant_data["ref"] = self.new_variant_data["cdot_ref"]
                self.new_variant_data["alt"] = self.new_variant_data["cdot_alt"]
            if "p_dot" in classification_json:
                pdot_m = parse_pdot(classification_json["p_dot"])
                if pdot_m:
                    pdot_m["pdot"] = get_pdot_abbreviation(pdot_m["pdot"])
                self.new_variant_data.update(pdot_m)
            if "transcript" in classification_json:
                self.new_variant_data.update(parse_transcript(classification_json["transcript"]))
            self.complete = True

            url = f"https://franklin.genoox.com/clinical-db/variant/snp/{chrom}-{pos}-{ref}-{alt}"
            self.html_links["main"] = SourceURL("Go", url)
        else:
            self.complete = False

        self.html_text = self.new_variant_data.get("franklin_classification", "Not found")

    async def rs(self):
        rs = self.variant["rs"]

        response, response_json = await self.get_parse_search_response(rs)
        await self.process(response_json)
        
    
    async def transcript_cdot(self):
        transcript = self.variant["transcript"]
        cdot = self.variant["cdot"]

        transcript_cdot = f"{transcript}:{cdot}"

        response, response_json = await self.get_parse_search_response(transcript_cdot)
        await self.process(response_json)

    async def gene_cdot(self):
        gene = self.variant["gene"]
        cdot = self.variant["gene_cdot"]

        gene_cdot = f"{gene}:{cdot}"

        response, response_json = await self.get_parse_search_response(gene_cdot)
        await self.process(response_json)



    async def chr_pos_ref_alt(self):
        chrom = self.variant["chr"]
        pos = self.variant["pos"]
        ref = self.variant["ref"]
        alt = self.variant["alt"]

        chr_pos_ref_alt = f"{chrom} {pos} {ref} {alt}"
        response, response_json = await self.get_parse_search_response(chr_pos_ref_alt)
        await self.process(response_json)

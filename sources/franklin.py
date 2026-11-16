import asyncio
from typing import Any

import aiohttp

from search import parse_cdot, parse_pdot, parse_transcript
from util import get_pdot_abbreviation
from .source_result import Source, SourceURL



# the somatic classification of Franklin (AMP/ASCO/CAP tiers), with the colors Franklin uses for them
SOMATIC_TIERS = {
    "TIER_1": ("Tier 1", "strong clinical significance", "#e03a39"),
    "TIER_2": ("Tier 2", "potential clinical significance", "#f19a29"),
    "TIER_3": ("Tier 3", "unknown clinical significance", "#919fa5"),
    "TIER_4": ("Tier 4", "benign or likely benign", "#1ab29c"),
}

ONCOGENIC_CLASSIFICATIONS = {
    "Oncogenic": "Oncogenic",
    "LikelyOncogenic": "Likely oncogenic",
    "VUS": "Uncertain significance",
    "LikelyBenign": "Likely benign",
    "Benign": "Benign",
}

# the (germline) ACMG classification of Franklin, with a color from green (benign) to red (pathogenic)
ACMG_CLASSIFICATIONS = {
    "Benign": ("Benign", "#2e8b3a"),
    "LikelyBenign": ("Likely benign", "#4b9f4b"),
    "VUS": ("Uncertain significance", "#d9822b"),
    "Uncertain": ("Uncertain significance", "#d9822b"),
    "LikelyPathogenic": ("Likely pathogenic", "#e8590c"),
    "Pathogenic": ("Pathogenic", "#d62828"),
}


class Franklin(Source):
    def set_entries(self):
        self.entries = {
            ("rs",): self.rs,
            ("transcript", "cdot"): self.transcript_cdot,
            ("gene", "gene_cdot"): self.gene_cdot,
            ("chr", "pos", "ref", "alt"): self.chr_pos_ref_alt,
        }

    async def get_parse_search_response(self, search: str) -> tuple[Any, Any]:
        """
        Helper function that handles some boiler plate needed for a Franklin API call
        """
        url = "https://franklin.genoox.com/api/parse_search"

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
        """
        Helper function that handles some boiler plate needed for a Franklin classification API call
        """
        url = "https://franklin.genoox.com/api/classify"
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

    async def get_somatic_classification(self, chrom, pos, ref, alt) -> dict:
        """
        Returns the somatic classification (the tier) and the oncogenic classification of the variant.
        Molclass is used for tumors, so these are shown instead of the (germline) ACMG classification.
        """
        variant = {"chrom": f"chr{chrom}", "pos": pos, "ref": ref, "alt": alt, "reference_version": "hg19"}
        headers = {"Content-Type": "application/json", "Cache-Control": "no-cache"}

        async def classification(url, post_data):
            try:
                _, resp = await self.async_post_json(url, json=post_data, headers=headers)
            except (TimeoutError, aiohttp.ClientError):
                self.timeout = False  # the card is still useful without it
                return None
            return resp.get("classification") if isinstance(resp, dict) else None

        tier, oncogenic = await asyncio.gather(
            classification("https://franklin.genoox.com/api/somatic/classify", {"snp_variant": variant}),
            classification("https://franklin.genoox.com/api/classify_oncogenic", {"is_versioned_request": False, "variant": variant}),
        )
        return {"tier": tier, "oncogenic": oncogenic}

    def get_somatic_html(self, somatic: dict, acmg: str | None = None) -> str:
        """
        The somatic tier, the oncogenicity and the (germline) ACMG classification of Franklin, one per line
        """
        lines = []
        if somatic.get("tier") in SOMATIC_TIERS:
            name, meaning, color = SOMATIC_TIERS[somatic["tier"]]
            lines.append(f"<b style='color: {color}'>{name}</b> {meaning}")
        if somatic.get("oncogenic") in ONCOGENIC_CLASSIFICATIONS:
            lines.append(f"<span class='small'>Oncogenicity: {ONCOGENIC_CLASSIFICATIONS[somatic['oncogenic']]}</span>")
        if acmg in ACMG_CLASSIFICATIONS:
            name, color = ACMG_CLASSIFICATIONS[acmg]
            lines.append(f"<span class='small'>Pathogenicity (ACMG): <b style='color: {color}'>{name}</b></span>")
        return "<br />".join(lines) or "No classification"

    def get_classification_color(self, classification):
        """
        Returns a color for the different possible classification Franklin can give
        """
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
        """
        Takes the search response performed by the different entries and performs 
        secondary queries for more detailed variant meta data and a classification value
        """
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
            
            # follow up query for more variant meta data with the 'best variant option'
            variant_detail_url = f"https://franklin.genoox.com/api/fetch_variant_details?chr=chr{chrom}&pos={pos}&ref={ref}&alt={alt}&reference_version=hg19"
            variant_detail_data = {
                "chr": chrom,
                "pos": pos,
                "ref": ref,
                "alt": alt,
                "reference_version": "hg19"
            }
            headers = {
                'Content-Type': "application/json",
                'Cache-Control': "no-cache",
            }
            _, franklin_variant_detail = await self.async_post_json(
                variant_detail_url, 
                json=variant_detail_data,
                headers=headers
            )

            if "rs" in franklin_variant_detail:
                self.new_variant_data["rs"] = franklin_variant_detail["rs"]

            if "db_snp" in franklin_variant_detail:
                self.new_variant_data["rs"] = franklin_variant_detail["db_snp"]

            if "transcript" in franklin_variant_detail:
                self.new_variant_data["transcript"] = franklin_variant_detail["transcript"]

            if "gene" in franklin_variant_detail:
                self.new_variant_data["gene"] = franklin_variant_detail["gene"]

            # the (ACMG) classification also has the gene, cdot and pdot of the variant
            classification_json, somatic = await asyncio.gather(
                self.get_classification_response(chrom, pos, ref, alt),
                self.get_somatic_classification(chrom, pos, ref, alt),
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

            url = f"https://franklin.genoox.com/clinical-db/variant/snp/{chrom}-{pos}-{ref}-{alt}?app=publications"
            self.html_links["main"] = SourceURL("Publications", url)
            self.html_text = self.get_somatic_html(somatic, franklin_classification)
        else:
            self.complete = False
            self.html_text = "Not found"

    async def rs(self):
        rs = self.variant["rs"]

        _, response_json = await self.get_parse_search_response(rs)
        await self.process(response_json)
        
    
    async def transcript_cdot(self):
        transcript = self.variant["transcript"]
        cdot = self.variant["cdot"]

        transcript_cdot = f"{transcript}:{cdot}"

        _, response_json = await self.get_parse_search_response(transcript_cdot)
        await self.process(response_json)

    async def gene_cdot(self):
        gene = self.variant["gene"]
        cdot = self.variant["gene_cdot"]

        gene_cdot = f"{gene}:{cdot}"

        _, response_json = await self.get_parse_search_response(gene_cdot)
        await self.process(response_json)



    async def chr_pos_ref_alt(self):
        chrom = self.variant["chr"]
        pos = self.variant["pos"]
        ref = self.variant["ref"]
        alt = self.variant["alt"]

        chr_pos_ref_alt = f"{chrom} {pos} {ref} {alt}"
        _, response_json = await self.get_parse_search_response(chr_pos_ref_alt)
        await self.process(response_json)

from .source_result import Source, SourceURL



class Franklin(Source):
    def set_entries(self):
        self.entries = {
            ("rs",): self.rs,
            ("transcript", "cdot"): self.transcript_cdot,
            ("chr", "pos", "ref", "alt"): self.chr_pos_ref_alt,
        }

    async def get_parse_search_response(self, search: str) -> dict:
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
        return resp
    
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
    
    async def process(self, response_json):
        if "best_variant_option" in response_json:
            variant = response_json["best_variant_option"]
            self.new_variant_data["chr"] = variant["chrom"].replace("chr", "")
            self.new_variant_data["pos"] = variant["pos"]
            self.new_variant_data["ref"] = variant["ref"]
            self.new_variant_data["alt"] = variant["alt"]

            full_variant = variant["to_full_variant"]
            self.new_variant_data["start"] = full_variant["start"]
            self.new_variant_data["end"] = full_variant["end"]

            
            url = f"https://franklin.genoox.com/clinical-db/variant/snp/{variant['chrom']}-{variant['pos']}-{variant['ref']}-{variant['alt']}"

            classification_json = await self.get_classification_response(
                self.new_variant_data["chr"], 
                self.new_variant_data["pos"], 
                self.new_variant_data["ref"], 
                self.new_variant_data["alt"]
            )

            self.new_variant_data["franklin_classification"] = classification_json.get("classification", "Unknown")
            
            if "gene" in classification_json:
                self.new_variant_data["gene"] = classification_json["gene"]
            if "c_dot" in classification_json:
                self.new_variant_data["cdot"] = classification_json["c_dot"]
            if "p_dot" in classification_json:
                self.new_variant_data["pdot"] = classification_json["p_dot"]
            if "transcript" in classification_json:
                self.new_variant_data["transcript"] = classification_json["transcript"]
            self.complete = True
        else:
            self.complete = False

        self.html_links["main"] = SourceURL("Go", url)
        self.html_text = self.new_variant_data.get("franklin_classification", "NA")

    async def rs(self):
        rs = self.variant["rs"]

        response_json = await self.get_parse_search_response(rs)
        await self.process(response_json)
        
    
    async def transcript_cdot(self):
        transcript = self.variant["transcript"]
        cdot = self.variant["cdot"]

        transcript_cdot = f"{transcript}:{cdot}"

        response_json = await self.get_parse_search_response(transcript_cdot)
        await self.process(response_json)

    async def chr_pos_ref_alt(self):
        chrom = self.variant["chr"]
        pos = self.variant["pos"]
        ref = self.variant["ref"]
        alt = self.variant["alt"]

        chr_pos_ref_alt = f"{chrom} {pos} {ref} {alt}"
        response_json = await self.get_parse_search_response(chr_pos_ref_alt)
        await self.process(response_json)

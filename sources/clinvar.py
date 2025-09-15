from typing import Any

import httpx
from icecream import ic
from jinja2 import BaseLoader, Environment
from models import VariantData
from pydantic import BaseModel
from search import parse_search
from util import get_pdot_abbreviation

from .source_result import Source, SourceURL

ic.configureOutput(prefix="debug-", includeContext=True)

SUMMARY_TABLE_TEMPLATE = """
<table class='table'>
<tr>
    <th>Classification</th>
    <th>SCV Sources</th>
</tr>
<tr>
    <td>{{ data["classification"] }}</td>
    <td>{{ data["source"] }}</td>
</tr>
</table>
"""


class ClinVarAPIResponse(BaseModel):
    status: int
    ids: list[str]
    data: dict[str, list[Any]]
    results: list[list[str]]


class TemplateData(BaseModel):
    clinical_significance: str | None = None
    number_submissions: int | None = None


class ClinVar(Source):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api_url = "https://clinicaltables.nlm.nih.gov/api/variants/v4/search"
        self.clingen_url = "https://reg.clinicalgenome.org/redmine/projects/registry/genboree_registry/by_caid?caid="
        self.rs_url = "https://www.ncbi.nlm.nih.gov/snp/"

    def set_entries(self):
        self.entries = {
            (
                "transcript",
                "pos",
            ): self.transcript_cdot,  # TODO removing this bricks clinvar wth ?
            ("transcript", "cdot"): self.transcript_cdot,
            # ("chr", "pos", "ref", "alt"): self.chr_pos_ref_alt,
            # ("chr", "pos"): self.chr_pos,
        }
        return self.entries

    async def process(self):
        if "rs" in self.variant:
            rs = self.variant["rs"]
            clinvar_miner_url = f"https://clinvarminer.genetics.utah.edu/search?q={rs}"
            self.html_links["miner"] = SourceURL("miner", clinvar_miner_url)
            self.complete = False

        self.html_links["main"] = SourceURL("Go", self.clinvar_url)

        api_data = await self.get_api_results()
        self.api_html_data = self.map_api_html_data(api_data)
        self.api_variant_data = self.map_api_results(api_data)

        if (
            self.variant["transcript_version"]
            != self.api_variant_data.transcript_version
        ):
            self.matches_consensus = False
            warning_str = (
                f"Result for {self.api_variant_data.transcript} (different version)"
            )
            if warning_str not in self.matches_consensus_tooltip:
                self.matches_consensus_tooltip.append(warning_str)

        self.html_text = await self.html_template()
        self.new_variant_data.update(self.api_variant_data)
        self.complete = True

    async def get_api_results(self) -> ClinVarAPIResponse:
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                raw_response = await client.get(self.api_url, params=self.params)
                raw_response.raise_for_status()
                # response = ClinVarAPIResponse.validate(raw_response)
                json = raw_response.json()
                response = {
                    "status": json[0],
                    "ids": json[1],
                    "data": json[2],
                    "results": json[3],
                }

                response = ClinVarAPIResponse.parse_obj(response)
                return response
        except httpx.HTTPStatusError as e:
            self.log_error(f"HTTP error fetching from API: {e.response.status_code}")
            raise
        except httpx.RequestError as e:
            self.log_error(f"Request error fetching from API: {e}")
            raise
        except Exception as e:
            ## log
            self.log_error(f"Unexpected error fetching from API: {e}")
            raise

    def map_api_results(self, api_data: ClinVarAPIResponse) -> VariantData:
        """Map new API response to legacy structure with safe extraction"""
        data = api_data.data
        parsed_name = parse_search(self._get(data, "Name"))
        if "pdot" in parsed_name:
            parsed_name["pdot"] = get_pdot_abbreviation(parsed_name["pdot"])
        clingen_id = next(
            (
                item.split(":")[1]
                for item in data.get("OtherIDs") or []
                if item.startswith("ClinGen")
            ),
            None,
        )
        clingen_url = f"{self.clingen_url + clingen_id}" if clingen_id else None
        rs = self._get(data, "dbSNP")
        rs_url = f"{self.rs_url + rs}" if rs else None

        return VariantData(
            **parsed_name,
            chr=self._get(data, "Chromosome"),
            clingen_id=clingen_id,
            clingen_url=clingen_url,
            gene=self._get(data, "GeneSymbol"),
            pos=self._get(data, "Start"),
            rs=rs,
            rs_url=rs_url,
            to=self._get(data, "Stop"),
        )

    def map_api_html_data(self, api_data: ClinVarAPIResponse) -> dict[str, str]:
        data = api_data.data

        clin = self._get(data, "ClinicalSignificance") or ""
        source = self._get(data, "NumberSubmitters") or ""

        return {
            "classification": clin,
            "source": source,
        }

    async def html_template(self):
        template = Environment(loader=BaseLoader).from_string(SUMMARY_TABLE_TEMPLATE)
        return template.render(data=self.api_html_data)

    async def transcript_cdot(self):
        transcript = self.variant["transcript"].split(".")[0]
        cdot = self.variant["cdot"]

        transcript_cdot = f"{transcript}:{cdot}"

        self.clinvar_url = (
            f"https://www.ncbi.nlm.nih.gov/clinvar/?term={transcript_cdot}"
        )
        self.params = {
            "terms": transcript_cdot,
            "sf": "Name",
            "ef": "AminoAcidChange,Chromosome,dbSNP,NucleotideChange,Start,Stop,Name,GeneSymbol,ClinicalSignificance,ReviewStatus,HGVS_c,HGVS_p,OtherIDs,NumberSubmitters",
            "q": f'NucleotideChange:"{cdot}"',
            "max": "10",
        }

        await self.process()

    async def chr_pos_ref_alt(self):
        chrom = self.variant["chr"]
        pos = self.variant["pos"]
        ref = self.variant["ref"]
        alt = self.variant["alt"]
        clinvar_term = f"{chrom}[CHR]+AND+{pos}[chrpos37]+{ref}>{alt}"
        self.clinvar_url = f"https://www.ncbi.nlm.nih.gov/clinvar/?term={clinvar_term}"
        self.params = {
            "terms": clinvar_term,
            "sf": "Name",
            "ef": "AminoAcidChange,Chromosome,dbSNP,NucleotideChange,Start,Stop,Name,GeneSymbol,ClinicalSignificance,ReviewStatus,HGVS_c,HGVS_p,OtherIDs,NumberSubmitters",
            "q": f'Chromosome:"{chrom}" AND Start:"{pos}" AND ReferenceAllele:"{ref}" AND AlternateAllele:"{alt}"',
            "max": "10",
        }
        await self.process()

    async def chr_pos(self):
        chrom = self.variant["chr"]
        pos = self.variant["pos"]
        clinvar_term = f"{chrom}[CHR]+AND+{pos}[chrpos37]"
        self.clinvar_url = f"https://www.ncbi.nlm.nih.gov/clinvar/?term={clinvar_term}"
        self.params = {
            "terms": clinvar_term,
            "sf": "Name",
            "ef": "AminoAcidChange,Chromosome,dbSNP,NucleotideChange,Start,Stop,Name,GeneSymbol,ClinicalSignificance,ReviewStatus,HGVS_c,HGVS_p,OtherIDs,NumberSubmitters",
            "q": f'Chromosome:"{chrom}" AND Start:"{pos}"',
            "max": "10",
        }
        await self.process()

    def _get(self, data: dict, key: str) -> str | None:
        value = data.get(key)
        return value[0] if value and len(value) > 0 and value[0] != "" else None

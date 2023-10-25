import json
import re

from yaml import parse

from search import parse_search
from util import get_pdot_abbreviation

from .source_result import Source, SourceURL

HEADER_GENE_RE = re.compile("\((?!p\.)(?P<gene>[^\)]+)", re.IGNORECASE)
JSOND_RE = re.compile('href="(?P<url>/allele/[^"]+)"')

class GnomAD(Source):
    def set_entries(self):
        self.entries = {
            ("chr", "pos", "ref", "alt"): self.chr_pos_ref_alt,
        }

    def is_hidden(self) -> bool:
        return True

    async def chr_pos_ref_alt(self):
        """
        Queries the Gnomad API and adds the meta data
        """
        chrom = self.variant["chr"]
        pos = self.variant["pos"]
        ref = self.variant["ref"]
        alt = self.variant["alt"]

        api_url = f"https://gnomad.broadinstitute.org/api/"
        query = f"{chrom}-{pos}-{ref}-{alt}"
        json_data = '{"query":"\nquery GnomadVariant($variantId: String!, $datasetId: DatasetId!, $referenceGenome: ReferenceGenomeId!, $includeLocalAncestry: Boolean!, $includeLiftoverAsSource: Boolean!, $includeLiftoverAsTarget: Boolean!) {\n  variant(variantId: $variantId, dataset: $datasetId) {\n    variant_id\n    reference_genome\n    chrom\n    pos\n    ref\n    alt\n    caid\n    colocated_variants\n    coverage {\n      exome {\n        mean\n      }\n      genome {\n        mean\n      }\n    }\n    multi_nucleotide_variants {\n      combined_variant_id\n      changes_amino_acids\n      n_individuals\n      other_constituent_snvs\n    }\n    exome {\n      ac\n      an\n      ac_hemi\n      ac_hom\n      faf95 {\n        popmax\n        popmax_population\n      }\n      filters\n      populations {\n        id\n        ac\n        an\n        ac_hemi\n        ac_hom\n      }\n      local_ancestry_populations @include(if: $includeLocalAncestry) {\n        id\n        ac\n        an\n      }\n      age_distribution {\n        het {\n          bin_edges\n          bin_freq\n          n_smaller\n          n_larger\n        }\n        hom {\n          bin_edges\n          bin_freq\n          n_smaller\n          n_larger\n        }\n      }\n      quality_metrics {\n        allele_balance {\n          alt {\n            bin_edges\n            bin_freq\n            n_smaller\n            n_larger\n          }\n        }\n        genotype_depth {\n          all {\n            bin_edges\n            bin_freq\n            n_smaller\n            n_larger\n          }\n          alt {\n            bin_edges\n            bin_freq\n            n_smaller\n            n_larger\n          }\n        }\n        genotype_quality {\n          all {\n            bin_edges\n            bin_freq\n            n_smaller\n            n_larger\n          }\n          alt {\n            bin_edges\n            bin_freq\n            n_smaller\n            n_larger\n          }\n        }\n        site_quality_metrics {\n          metric\n          value\n        }\n      }\n    }\n    genome {\n      ac\n      an\n      ac_hemi\n      ac_hom\n      faf95 {\n        popmax\n        popmax_population\n      }\n      filters\n      populations {\n        id\n        ac\n        an\n        ac_hemi\n        ac_hom\n      }\n      local_ancestry_populations @include(if: $includeLocalAncestry) {\n        id\n        ac\n        an\n      }\n      age_distribution {\n        het {\n          bin_edges\n          bin_freq\n          n_smaller\n          n_larger\n        }\n        hom {\n          bin_edges\n          bin_freq\n          n_smaller\n          n_larger\n        }\n      }\n      quality_metrics {\n        allele_balance {\n          alt {\n            bin_edges\n            bin_freq\n            n_smaller\n            n_larger\n          }\n        }\n        genotype_depth {\n          all {\n            bin_edges\n            bin_freq\n            n_smaller\n            n_larger\n          }\n          alt {\n            bin_edges\n            bin_freq\n            n_smaller\n            n_larger\n          }\n        }\n        genotype_quality {\n          all {\n            bin_edges\n            bin_freq\n            n_smaller\n            n_larger\n          }\n          alt {\n            bin_edges\n            bin_freq\n            n_smaller\n            n_larger\n          }\n        }\n        site_quality_metrics {\n          metric\n          value\n        }\n      }\n    }\n    flags\n    lof_curations {\n      gene_id\n      gene_symbol\n      verdict\n      flags\n      project\n    }\n    rsids\n    transcript_consequences {\n      domains\n      gene_id\n      gene_version\n      gene_symbol\n      hgvs\n      hgvsc\n      hgvsp\n      is_canonical\n      is_mane_select\n      is_mane_select_version\n      lof\n      lof_flags\n      lof_filter\n      major_consequence\n      polyphen_prediction\n      sift_prediction\n      transcript_id\n      transcript_version\n    }\n    in_silico_predictors {\n      id\n      value\n      flags\n    }\n  }\n\n  clinvar_variant(variant_id: $variantId, reference_genome: $referenceGenome) {\n    clinical_significance\n    clinvar_variation_id\n    gold_stars\n    last_evaluated\n    review_status\n    submissions {\n      clinical_significance\n      conditions {\n        name\n        medgen_id\n      }\n      last_evaluated\n      review_status\n      submitter_name\n    }\n  }\n\n  liftover(source_variant_id: $variantId, reference_genome: $referenceGenome) @include(if: $includeLiftoverAsSource) {\n    liftover {\n      variant_id\n      reference_genome\n    }\n    datasets\n  }\n\n  liftover_sources: liftover(liftover_variant_id: $variantId, reference_genome: $referenceGenome) @include(if: $includeLiftoverAsTarget) {\n    source {\n      variant_id\n      reference_genome\n    }\n    datasets\n  }\n\n  meta {\n    clinvar_release_date\n  }\n}\n","variables":{"datasetId":"gnomad_r2_1","includeLocalAncestry":false,"includeLiftoverAsSource":true,"includeLiftoverAsTarget":false,"referenceGenome":"GRCh37","variantId":"' + query + '"}}'

        resp, api_json = await self.async_get_json(api_url, json=json_data)

        if "errors" in api_json:
            errors = api_json["errors"]
            for error in errors:
                if error["message"] == "Variant not found":
                    self.found = False
                    self.log_warning("Variant not found")
                    return
        
        if "data" not in api_json:
            self.log_warning("No 'data' in api json")
            return

        data = api_json["data"]
        
        if "variant" not in data:
            self.log_warning("No 'variant' in data json")
            return

        variant = data["variant"]
        if "chrom" in variant:
            self.new_variant_data["chr"] = variant["chrom"]
        if "pos" in variant:
            self.new_variant_data["pos"] = variant["pos"]
        if "pos" in variant:
            self.new_variant_data["ref"] = variant["alt"]
        if "pos" in variant:
            self.new_variant_data["pos"] = variant["pos"]
            
        
        
        

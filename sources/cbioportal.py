from .source_result import Source, SourceURL

class cBioPortal(Source):
    def set_entries(self):
        self.entries = {
            ("gene", ): self.gene,
        }
    
    async def gene(self):
        """
        Simply add a URL to the gene
        """
        gene = self.variant["gene"]
        url = f"http://www.cbioportal.org/results/mutations?cancer_study_list=laml_tcga_pan_can_atlas_2018%2Cacc_tcga_pan_can_atlas_2018%2Cblca_tcga_pan_can_atlas_2018%2Clgg_tcga_pan_can_atlas_2018%2Cbrca_tcga_pan_can_atlas_2018%2Ccesc_tcga_pan_can_atlas_2018%2Cchol_tcga_pan_can_atlas_2018%2Ccoadread_tcga_pan_can_atlas_2018%2Cdlbc_tcga_pan_can_atlas_2018%2Cesca_tcga_pan_can_atlas_2018%2Cgbm_tcga_pan_can_atlas_2018%2Chnsc_tcga_pan_can_atlas_2018%2Ckich_tcga_pan_can_atlas_2018%2Ckirc_tcga_pan_can_atlas_2018%2Ckirp_tcga_pan_can_atlas_2018%2Clihc_tcga_pan_can_atlas_2018%2Cluad_tcga_pan_can_atlas_2018%2Clusc_tcga_pan_can_atlas_2018%2Cmeso_tcga_pan_can_atlas_2018%2Cov_tcga_pan_can_atlas_2018%2Cpaad_tcga_pan_can_atlas_2018%2Cpcpg_tcga_pan_can_atlas_2018%2Cprad_tcga_pan_can_atlas_2018%2Csarc_tcga_pan_can_atlas_2018%2Cskcm_tcga_pan_can_atlas_2018%2Cstad_tcga_pan_can_atlas_2018%2Ctgct_tcga_pan_can_atlas_2018%2Cthym_tcga_pan_can_atlas_2018%2Cthca_tcga_pan_can_atlas_2018%2Cucs_tcga_pan_can_atlas_2018%2Cucec_tcga_pan_can_atlas_2018%2Cuvm_tcga_pan_can_atlas_2018&Z_SCORE_THRESHOLD=2.0&RPPA_SCORE_THRESHOLD=2.0&profileFilter=mutations%2Cfusion%2Cgistic&case_set_id=all&gene_list={gene}&geneset_list=%20&tab_index=tab_visualize&Action=Submit"
        self.html_links["main"] = SourceURL("Go", url)
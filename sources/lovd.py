from lxml import etree
from .source_result import Source, SourceURL

class LOVD(Source):
    def set_entries(self):
        self.entries = {
            ("gene", ): self.gene,
            ("gene", "cdot"): self.gene_cdot,
        }

    async def gene(self):
        gene = self.variant["gene"]
        url = f"https://databases.lovd.nl/shared/variants/{gene}/unique"

        self.html_links["main"] = SourceURL("Go", url)

    async def gene_cdot(self):
        gene = self.variant["gene"]
        url = f"https://databases.lovd.nl/shared/variants/{gene}/unique"
        self.html_links["main"] = SourceURL("Go", url)
        
        cdot = self.variant["cdot"]

        resp, lovd_text = await self.async_get_text(url)
        tree = etree.HTML(bytes(lovd_text, encoding='utf8'))
        transcript_id_input = tree.xpath("//input[@name='search_transcriptid']")
        if not transcript_id_input:
            self.log_warning("Could not extract transcript_id from lovd page")
            return
        
        transcript_id_input = transcript_id_input[0]
        transcript_id = transcript_id_input.get("value")

        view_list_id = f"CustomVL_VOTunique_VOG_{gene}"
        objct = "Custom_ViewList"
        object_id = "VariantOnTranscriptUnique,VariantOnGenome"
        page = 1
        cdot_url = None
        encoded_cdot = cdot.replace("&", "&gt;")
        while not cdot_url:
            table_url = f"https://databases.lovd.nl/shared/ajax/viewlist.php?viewlistid={view_list_id}&object={objct}&object_id={object_id}&id={gene}&search_transcriptid={transcript_id}&page_size=1000&page={page}"
            resp, lovd_page = await self.async_get_text(table_url)
            tree = etree.HTML(bytes(lovd_page, encoding="utf8"))
            any_rows_on_page = tree.xpath("//tr[@data-href]")
            if not any_rows_on_page:
                break

            cdot_link = tree.xpath(f"//a[text()='{encoded_cdot}']")
            if cdot_link:
                cdot_link = cdot_link[0]
                cdot_url = f"https://databases.lovd.nl/shared/{cdot_link.get('href')}"
                print(cdot_url)
                break
            page += 1
        if cdot_url:
            self.html_links["Gene"] = SourceURL("Gene", self.html_links["main"].url)
            self.html_links["main"] = SourceURL("Go", cdot_url) 
        #  https://databases.lovd.nl/shared/ajax/viewlist.php?viewlistid=CustomVL_VOTunique_VOG_PIK3CA&object=Custom_ViewList&object_id=VariantOnTranscriptUnique%2CVariantOnGenome&id=PIK3CA&order=VariantOnTranscript%2FDNA%2CASC&search_transcriptid=00016173&page_size=1000&page=1
                
        # //tr[@data-href]

from bs4 import BeautifulSoup

from .source_result import Source, SourceURL


class COSMIC(Source):
    def set_entries(self):
        self.entries = {
            ("gene", "cdot"): self.gene_cdot,
            ("gene", ): self.gene,
        }

    async def gene(self):
        gene = self.variant["gene"]
        
        url = f"https://cancer.sanger.ac.uk/cosmic/gene/analysis?ln={gene}"

        self.html_links["main"] = SourceURL("Go", url)

    async def gene_cdot(self):
        gene = self.variant["gene"] 
        cdot = self.variant["cdot"]

        url = f"https://cancer.sanger.ac.uk/cosmic/gene/analysis?ln={gene}"

        self.html_links["main"] = SourceURL("Go", url)
        cookies = {
            "genome_version": "37"
        }
        response, response_html = await self.async_get_text(url, cookies=cookies)
        
        soup = BeautifulSoup(response_html, 'html.parser')

        inputs_form_ul = soup.find("ul", {"id": "filters-advanced"})
        if not inputs_form_ul:
            self.log_warning("Could not find start/end/id form on page")
            return
        
        inputs_form = inputs_form_ul.parent
        if not inputs_form:
            self.log_warning("Could not find start/end/id form on page")
            return

        # print(inputs_form)

        id_input = inputs_form.find("input", {"name": "id"})
        if not id_input:
            self.log_warning("Could not find id input on page")
            return

        gene_id = id_input.get("value")

        start_input = inputs_form.find("input", {"name": "start"})
        if start_input:
            start = start_input.get("value")
        else:
            self.log_warning("Could not find start input on page, continuing with start=1")
            start = "1"

        end_input = inputs_form.find("input", {"name": "end"})
        if end_input:
            end = end_input.get("value")
        else:
            self.log_warning("Could not find end input on page, continuing with end=100000000")
            end = "100000000"
        
        variant_url = f"https://cancer.sanger.ac.uk/cosmic/gene/mutations?end={end}&id={gene_id}&start={start}&sSearch={cdot}"
        self.log_debug(f"Cosmic variant url: {variant_url}")

        variant_headers = {
            "X-Requested-With": "XMLHttpRequest"
        }
        cookies = {
            "genome_version": "37"
        }
        response, variant_json = await self.async_get_json(variant_url, headers=variant_headers, cookies=cookies)
        if "aaData" not in variant_json:
            self.log_warning("Missing aaData key from variant_json")
            return
        
        aa_data = variant_json["aaData"]
        if len(aa_data) == 0:
            self.log_warning("No match found")
            return
        
        aa_data = aa_data[0]
        if len(aa_data) < 4:
            self.log_warning("Weird len of aa_data")
            return
        
        cosmic_id = aa_data[3]
        self.html_subtitle = cosmic_id
        self.html_links["main"] = SourceURL("Go", f"https://cancer.sanger.ac.uk/cosmic/search?q={cosmic_id}")


from templates import templates

import aiohttp
from .source_result import SourceResult, Source

def PMKB(variant: dict, request):
    url = ""
    if "gene" in variant:
        gene = variant["gene"]
        url = f"https://pmkb.weill.cornell.edu/search?search={gene}"

    return templates.get_template(
        "card.html.jinja2", 
    ).render(title="PMKB", text="", subtitle="", links=[{"url": url, "text": "Go"}])




async def PMKB_(session: aiohttp.ClientSession, variant: dict):
    gene = variant["gene"]
    url = f"https://pmkb.weill.cornell.edu/search?search={gene}"

    
    html = templates.get_template(
        "card.html.jinja2", 
    ).render(title="PMKB", text="", subtitle="", links=[{"url": url, "text": "Go"}])

    return SourceResult("PMKB", {}, html, True)

class _PMKB(Source):
    def set_entries(self):
        self.entries = {
            ("gene",): self.gene
        }

    async def gene(self):
        gene = self.variant["gene"]

        url = f"https://pmkb.weill.cornell.edu/search?search={gene}"
        self.set_html(title="PMKB", text="", subtitle="", links=[{"url": url, "text": "Go"}])
        self.complete = True
from templates import templates

import aiohttp
from .source_result import SourceResult

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

PMKB_entries = {
    ("gene",): PMKB_
}
from templates import templates

def PMKB(variant: dict, request):
    url = ""
    if "gene" in variant:
        gene = variant["gene"]
        url = f"https://pmkb.weill.cornell.edu/search?search={gene}"

    return templates.get_template(
        "card.html.jinja2", 
    ).render(title="PMKB", text="", subtitle="", links=[{"url": url, "text": "Go"}])




def PMKB_(variant: dict):
    gene = variant["gene"]
    url = f"https://pmkb.weill.cornell.edu/search?search={gene}"

    return variant, templates.get_template(
        "card.html.jinja2", 
    ).render(title="PMKB", text="", subtitle="", links=[{"url": url, "text": "Go"}])

PMKB_entries = {
    ("gene",): PMKB_
}
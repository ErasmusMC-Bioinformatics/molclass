from templates import templates

def OncoKB(variant: dict, request):
    url = ""
    if "gene" in variant:
        gene = variant["gene"]
        url = f"https://www.oncokb.org/gene/{gene}"

    return templates.get_template(
        "card.html.jinja2", 
    ).render(title="ClinvarMiner", text="", subtitle="", links=[{"url": url, "text": "Go"}])
from templates import templates

def Cosmic(variant: dict, request):
    url = ""
    if "gene" in variant:
        gene = variant["gene"]
        url = f"https://cancer.sanger.ac.uk/cosmic/gene/analysis?ln={gene}"
    
    return templates.get_template(
        "card.html.jinja2", 
    ).render(title="Cosmic", text="", subtitle="", links=[{"url": url, "text": "Go"}])
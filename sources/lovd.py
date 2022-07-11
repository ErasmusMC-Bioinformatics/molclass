from templates import templates

def lovd(variant: dict, request):
    url = ""
    if "gene" in variant:
        gene = variant["gene"]
        # https://databases.lovd.nl/shared/variants/TSC1/unique
        url = f"https://databases.lovd.nl/shared/variants/{gene}/unique"

    return templates.get_template(
        "card.html.jinja2", 
    ).render(title="LovD", text="", subtitle="", links=[{"url": url, "text": "Go"}])
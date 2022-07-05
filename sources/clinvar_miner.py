from templates import templates

def Clinvar_Miner(variant: dict, request):
    url = ""
    if "dbSNP" in variant:
        dbSNP = variant["dbSNP"]
        rs = dbSNP["rs"]

        url = f"https://clinvarminer.genetics.utah.edu/search?q={rs}"

    return templates.get_template(
        "card.html.jinja2", 
    ).render(title="ClinvarMiner", text="", subtitle="", links=[{"url": url, "text": "Go"}])
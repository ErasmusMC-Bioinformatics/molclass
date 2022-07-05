from fastapi.templating import Jinja2Templates
from bs4 import BeautifulSoup

import requests

templates = Jinja2Templates(directory="templates")

def dbSNP(variant: dict, request):
    url = ""
    if "dbSNP" not in variant:
        return templates.get_template(
            "card.html.jinja2", 
        ).render(title="dbSNP", text="No rs# found", subtitle="-", links=[])

    dbSNP = variant["dbSNP"]
    rs = dbSNP["rs"]

    url = f"https://www.ncbi.nlm.nih.gov/snp/{rs}"

    response = requests.get(url)

    if response.status_code != 200:
        return templates.get_template(
            "card.html.jinja2", 
        ).render(title="dbSNP", text="Could not load URL", subtitle="-", links=[{"url": url, "text": "Go"}])

    soup = BeautifulSoup(response.text, "html.parser")

    clinical_sign_table = soup.find("table", {"id": "clinical_significance_datatable"})
    clinical_sign_tbody = clinical_sign_table.find("tbody")

    card_text = ""
    for row in clinical_sign_tbody.find_all("tr"):
        cols = row.find_all("td")
        cols = [e.text.strip() for e in cols]

        card_text += f"""<a href="https://www.ncbi.nlm.nih.gov/clinvar/{cols[0]}/">{cols[2]}</a><br />"""

    return templates.get_template(
        "card.html.jinja2", 
    ).render(title="dbSNP", text=card_text, subtitle=rs, links=[{"url": url, "text": "Go"}])


    
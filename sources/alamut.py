import json

import requests

from templates import templates

def Alamut(variant: dict, request) -> str:
    url = ""
    urls = []
    variant_set = set(variant)
    if set(["chr", "pos"]).issubset(variant_set):
        chrom = variant["chr"]
        pos = variant["pos"]
        url = f"http://127.0.0.1:10000/search?institution=ANL0016&apikey=18565976&request=chr{chrom}:{pos}"
        urls.append({"url": url, "text": "Pos"})

    if "dbSNP" in variant:
        db_snp_url = f"http://127.0.0.1:10000/search?institution=ANL0016&apikey=18565976&request={variant['dbSNP']['rs']}"
        urls.append({
            "url": db_snp_url, "text": "rs#"
        })

    if "gene" in variant:
        if "transcript" in variant:
            transcript = variant["transcript"]
            gene_url = f"http://127.0.0.1:10000/search?institution=ANL0016&apikey=18565976&request={variant['gene']} {transcript}"
        else:
            gene_url = f"http://127.0.0.1:10000/search?institution=ANL0016&apikey=18565976&request={variant['gene']}"
        urls.append({
            "url": gene_url, "text": "Gene"
        })
    
    if "transcript" in variant and "cdot" in variant:
        transcript = variant["transcript"]
        cdot = variant["cdot"]
        url = f"http://127.0.0.1:10000/search?institution=ANL0016&apikey=18565976&request={transcript}:{cdot}"
        urls.append({
            "url": url, "text": "Transcript:cdot"
        })
    
    return templates.get_template(
        "card.html.jinja2", 
    ).render(title="Alamut", text="", subtitle="", links=urls)
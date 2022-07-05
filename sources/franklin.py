import json

import requests

from templates import templates

def Franklin(variant: dict, request) -> str:
    url = ""
    variant_set = set(variant)
    if set(["chr", "pos", "ref", "alt"]).issubset(variant_set):
        chrom = variant["chr"]
        pos = variant["pos"]
        ref = variant["ref"]
        alt = variant["alt"]
        url = f"https://franklin.genoox.com/clinical-db/variant/snp/chr{chrom}-{pos}-{ref}-{alt}"
    # return {}
    franklin_classify_url = f"https://franklin.genoox.com/api/classify"
    post_data = f"{{\"is_versioned_request\":false,\"variant\":{{\"chrom\":{chrom},\"pos\":{pos},\"ref\":\"{ref}\",\"alt\":\"{alt}\",\"reference_version\":\"hg19\"}}}}"
    headers = {
        'Content-Type': "application/json",
        'Cache-Control': "no-cache",
    }
    
    response = requests.post(franklin_classify_url, data=post_data, headers=headers)

    if response.status_code != 200:
        return templates.get_template(
            "card.html.jinja2", 
        ).render(title="Franklin", text=response.text, subtitle=f"{response.status_code}", links=[{"url": url, "text": "Go"}])

    response_json = response.json()

    classification = response_json["classification"]
    
    return templates.get_template(
        "card.html.jinja2", 
    ).render(title="Franklin", text=classification, subtitle="", links=[{"url": url, "text": "Go"}])
import json

import requests
import aiohttp
from .source_result import SourceResult

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
    return templates.get_template(
        "card.html.jinja2", 
    ).render(title="Franklin", text="NCBI down?", subtitle="?", links=[{"url": url, "text": "Go"}])

async def get_parse_search_response(session: aiohttp.ClientSession, search: str) -> dict:
    url = f"https://franklin.genoox.com/api/parse_search"

    post_data = {
        "reference_version": "hg19",
        "search_text_input": search
    }
    headers = {
        'Content-Type': "application/json",
        'Cache-Control': "no-cache",
    }

    async with session.post(url, json=post_data, headers=headers) as response:
        resp = await response.json()
        return resp

async def get_classification_response(session: aiohttp.ClientSession, chrom, pos, ref, alt) -> dict:
    url = f"https://franklin.genoox.com/api/classify"
    post_data = {
        "is_versioned_request":False,
        "variant":{
            "chrom":chrom,
            "pos": pos,
            "ref":ref,
            "alt":alt,
            "reference_version":"hg19"
        }
    }
    headers = {
        'Content-Type': "application/json",
        'Cache-Control': "no-cache",
    }
    async with session.post(url, json=post_data, headers=headers) as response:
        resp = await response.json()
        return resp

async def Franklin_rs(session: aiohttp.ClientSession, variant: dict) -> dict:
    url = ""
    rs = variant["rs"]
    new_variant_data = {}

    response_json = await get_parse_search_response(session, rs)
    
    if "best_variant_option" in response_json:
        
        variant = response_json["best_variant_option"]
        new_variant_data["chr"] = variant["chrom"].replace("chr", "")
        new_variant_data["pos"] = variant["pos"]
        new_variant_data["ref"] = variant["ref"]
        new_variant_data["alt"] = variant["alt"]

        full_variant = variant["to_full_variant"]
        new_variant_data["start"] = full_variant["start"]
        new_variant_data["end"] = full_variant["end"]
        
        url = f"https://franklin.genoox.com/clinical-db/variant/snp/{variant['chrom']}-{variant['pos']}-{variant['ref']}-{variant['alt']}"

        classification_json = await get_classification_response(
            session, 
            new_variant_data["chr"], 
            new_variant_data["pos"], 
            new_variant_data["ref"], 
            new_variant_data["alt"]
        )

        new_variant_data["franklin_classification"] = classification_json.get("classification", "Unknown")
    
    html = templates.get_template(
        "card.html.jinja2", 
    ).render(title="Franklin", text=new_variant_data.get("franklin_classification", "NA"), subtitle="", links=[{"url": url, "text": "Go"}])
    return SourceResult("Franklin", new_variant_data, html, True)

Franklin_entries = {
    ("rs",): Franklin_rs
}
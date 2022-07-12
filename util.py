import re
import html
from typing import Optional
import requests

from bs4 import BeautifulSoup

TRANSCRIPT_RE = "(?P<transcript>NM_?[0-9]+)"

# https://regex101.com/r/Hxag8o/1
C_DOT_RE = "(?P<cdot>c[.](?P<cdot_pos>[0-9*]+([_+-][0-9]+(-[0-9]+)?)?)(?P<cdot_from>[actg]+)?(?P<type>&gt;|[>]|del|ins)(?P<cdot_to>[actg]+))"

# https://regex101.com/r/Hxag8o/1
P_DOT_RE = "(?P<pdot>\s*[(]p[.](?P<pdot_from>[^0-9]+)(?P<pdot_pos>[0-9]+)(?P<pdot_to>[^\s\n]+))"

TRANSCRIPT_RE = "(?P<transcript>NM_?[0-9]+([.][0-9]+)?)"

CHR_POS_END_REF_ALT = re.compile("(?P<chr>(chr)?[0-9])+\s+(?P<pos>[0-9]+)\s+(?P<end>[0-9]+)?(?P<ref>[actg])\s+(?P<alt>[actg])", re.IGNORECASE)
TRANSCRIPT_C_DOT = re.compile(f"{TRANSCRIPT_RE}:{C_DOT_RE}", re.IGNORECASE)
GENE_C_DOT = re.compile(re.compile(f"[^:]+:{C_DOT_RE}", re.IGNORECASE))

# https://regex101.com/r/Hxag8o/1
HEADER_RE = re.compile(f"(?P<transcript>NM_?[0-9]+([.][0-9]+)?)[(](?P<gene>[^)]+)[)]:(?P<cdot>c[.](?P<cdot_pos>[0-9*]+([_+-][0-9]+(-[0-9]+)?)?)(?P<cdot_from>[actg]+)?(?P<type>&gt;|[>]|del|ins)(?P<cdot_to>[actg]+))(?P<pdot>\s*[(]p[.](?P<pdot_from>[^0-9]+)(?P<pdot_pos>[0-9]+)(?P<pdot_to>[^\s\n]+))?", re.IGNORECASE)
# HEADER_RE = re.compile(f"{TRANSCRIPT_RE}[(](?P<gene>[^)]+)[)]:{C_DOT_RE}{P_DOT_RE}", re.IGNORECASE)

RS_RE = re.compile("(?P<rs>rs[0-9]+)", re.IGNORECASE)
RS_URL_RE = re.compile(f"https://www.ncbi.nlm.nih.gov/snp/{RS_RE.pattern}")
CLINGEN_RE = re.compile("http://reg.clinicalgenome.org/redmine/projects/registry/genboree_registry/by_caid[?]caid=(?P<id>CA[0-9]+)", re.IGNORECASE)

# https://regex101.com/r/z4NYRj/1
GRCH37_POS_RE = re.compile(f"https://www.ncbi.nlm.nih.gov/variation/view/[?]chr=(?P<chr>[0-9]+)(&|&amp;)q=(&|&amp;)assm=GCF_000001405.25(&|&amp;)from=(?P<from>[0-9]+)(&|&amp;)to=(?P<to>[0-9]+)", re.IGNORECASE)

def parse_clinvar_html(clinvar_text) -> dict:
    result = {}
    header_match = HEADER_RE.search(clinvar_text)
    if header_match:
        result.update(**header_match.groupdict())
        result["cdot"] = html.unescape(result["cdot"])

    rs_match = RS_URL_RE.search(clinvar_text)
    if rs_match:
        result["dbSNP"] = {
            "rs": rs_match.group("rs"),
            "url": rs_match.group(0),
        }
    
    clingen_match = CLINGEN_RE.search(clinvar_text)
    if clingen_match:
        result["ClinGen"] = {
            "id": clingen_match.group("id"),
            "url": clingen_match.group(0)
        }

    pos_grch37_match = GRCH37_POS_RE.search(clinvar_text)
    if pos_grch37_match:
        result.update(**pos_grch37_match.groupdict())

    if "to" in result:
        result["pos"] = result["to"]

    return result

def chr_pos_end_ref_alt(variant_match) -> dict:
    result = {}
    chrom = variant_match.group('chr')
    pos = variant_match.group('pos')
    end = variant_match.group('end')
    ref = variant_match.group('ref')
    alt = variant_match.group('alt')
    
    end = f"{end}[chrpos37]+" if end else ""
    pos = f"{pos}[chrpos37]"
    chrom = f"{chrom}[CHR]"

    clinvar_query = f"{chrom}+{pos}+{end}{ref}+{alt}"
    clinvar_url = f"https://www.ncbi.nlm.nih.gov/clinvar/?term={clinvar_query}"

    clinvar_response = requests.get(clinvar_url)

    if clinvar_response.status_code != 200:
        print(f"{clinvar_response.status_code}: {clinvar_url}")
        return result

    clinvar_text = clinvar_response.text

    result.update(parse_clinvar_html(clinvar_text))

    return result


def transcript_c_dot(variant_match):
    result = {}

    clinvar_query = f"{variant_match.group(0)}"
    clinvar_url = f"https://www.ncbi.nlm.nih.gov/clinvar/?term={clinvar_query}"
    print(clinvar_url)

    clinvar_response = requests.get(clinvar_url)

    if clinvar_response.status_code != 200:
        print(f"{clinvar_response.status_code}: {clinvar_url}")
        return result

    clinvar_text = clinvar_response.text

    result.update(parse_clinvar_html(clinvar_text))

    return result

def gene_c_dot(variant_match):
    result = {}

    clinvar_query = f"{variant_match.group(0)}"
    clinvar_url = f"https://www.ncbi.nlm.nih.gov/clinvar/?term={clinvar_query}"

    clinvar_response = requests.get(clinvar_url)

    if clinvar_response.status_code != 200:
        print(f"{clinvar_response.status_code}: {clinvar_url}")
        return result

    clinvar_text = clinvar_response.text

    result.update(parse_clinvar_html(clinvar_text))

    return result

def rs_number(variant_match):
    result = {}

    clinvar_query = f"{variant_match.group(0)}"
    clinvar_url = f"https://www.ncbi.nlm.nih.gov/clinvar/?term={clinvar_query}"

    clinvar_response = requests.get(clinvar_url)

    if clinvar_response.status_code != 200:
        print(f"{clinvar_response.status_code}: {clinvar_url}")
        return result

    clinvar_text = clinvar_response.text

    result.update(parse_clinvar_html(clinvar_text))

    return result


def get_variant_from_string(variant_string: str) -> dict:
    """
    Should return a dict/Variant class with enough information to form a clinvar query
    """
    result = {}
    if m := CHR_POS_END_REF_ALT.match(variant_string):
        print(f"Matched CHR POS END REF ALT: {m.group(0)}")
        result.update(chr_pos_end_ref_alt(m))
    elif m := TRANSCRIPT_C_DOT.match(variant_string):
        print(f"Matched Transcript:cDot: {m.group(0)}")
        result.update(transcript_c_dot(m))
    elif m := RS_RE.match(variant_string):
        print(f"Matched rs#: {m.group(0)}")
        result.update(rs_number(m))
    elif m := GENE_C_DOT.match(variant_string):
        print(f"Matched Gene:cDot: {m.group(0)}")
        result.update(gene_c_dot(m))

    return result

def get_variant_from_string_from_franklin(variant_string: str) -> dict:
    franklin_parse_search_url = "https://franklin.genoox.com/api/parse_search"


def write_to_debug_file(text, file_path="/mnt/d/molclass_debug.txt"):
    with open(file_path, 'w') as file_handle:
        file_handle.write(text)
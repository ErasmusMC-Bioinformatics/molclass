import re
from typing import Optional
import requests

from bs4 import BeautifulSoup

CHR_POS_END_REF_ALT = re.compile("(?P<chr>(chr|CHR)?[0-9])+\s+(?P<pos>[0-9]+)\s+(?P<end>[0-9]+)?(?P<ref>[actgACTG])\s+(?P<alt>[actgACTG])")
HEADER_RE = re.compile("(?P<transcript>NM_?[0-9]+([.][0-9]+)?)[(](?P<gene>[^)]+)[)]:(?P<cdot>c[.](?P<cdot_pos>[0-9]+)(?P<cdot_from>[actgACTG])(&gt;|[>])(?P<cdot_to>[actgACTG]))\s*[(](?P<pdot>p[.](?P<pdot_from>[^0-9]+)(?P<pdot_pos>[0-9]+)(?P<pdot_to>[^)]+))")

RS_RE = re.compile("https://www.ncbi.nlm.nih.gov/snp/(?P<rs>rs1554820262)")
CLINGEN_RE = re.compile("http://reg.clinicalgenome.org/redmine/projects/registry/genboree_registry/by_caid[?]caid=(?P<id>CA[0-9]+)")
NM_RE = re.compile("NM_?[0-9]+([.][0-9]+)?")
def chr_pos_end_ref_alt(variant_match) -> dict:
    result = {}
    chrom = variant_match.group('chr')
    pos = variant_match.group('pos')
    end = variant_match.group('end')
    ref = variant_match.group('ref')
    alt = variant_match.group('alt')

    result.update(
        chr=chrom,
        pos=pos,
        end=end,
        ref=ref,
        alt=alt
    )
    
    end = f"{end}[chrpos37]+" if end else ""
    pos = f"{pos}[chrpos37]"
    chrom = f"{chrom}[CHR]"

    clinvar_query = f"{chrom}+{pos}+{end}{ref}+{alt}"
    clinvar_url = f"https://www.ncbi.nlm.nih.gov/clinvar/variation/523362/?oq={clinvar_query}"

    clinvar_response = requests.get(clinvar_url)

    if clinvar_response.status_code != 200:
        print(f"{clinvar_response.status_code}: {clinvar_url}")
        return result

    clinvar_text = clinvar_response.text

    header_match = HEADER_RE.search(clinvar_text)
    if header_match:
        result.update(**header_match.groupdict())

    rs_match = RS_RE.search(clinvar_text)
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

    return result


def get_variant_from_string(variant_string: str) -> dict:
    """
    Should return a dict/Variant class with enough information to form a clinvar query
    """
    result = {}
    if m := CHR_POS_END_REF_ALT.match(variant_string):
        result.update(chr_pos_end_ref_alt(m))

    return result


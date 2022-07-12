from templates import templates
import aiohttp
from .source_result import SourceResult

def Clinvar(variant: dict, request):
    url = ""
    if set(["chr", "pos"]).issubset(set(variant)):
        chrom = variant["chr"]
        pos = variant["pos"]
        ref = variant["ref"] if "ref" in variant else ""
        alt = variant["alt"] if "alt" in variant else ""
        refalt = f"+{ref}>{alt}" if ref and alt else ""
        url = f"https://www.ncbi.nlm.nih.gov/clinvar/?term={chrom}[CHR]+AND+{pos}[chrpos37]{refalt}"
    
    clinvar_miner_url = ""
    if "dbSNP" in variant:
        dbSNP = variant["dbSNP"]
        rs = dbSNP["rs"]

        clinvar_miner_url = f"https://clinvarminer.genetics.utah.edu/search?q={rs}"

    return templates.get_template(
        "card.html.jinja2", 
    ).render(title="Clinvar", text="", subtitle="", links=[{"url": url, "text": "Go"}, {"url": clinvar_miner_url, "text": "Miner"}])

async def Clinvar_chr_pos(session: aiohttp.ClientSession, variant: dict):
    url = ""
    chrom = variant["chr"]
    pos = variant["pos"]
    url = f"https://www.ncbi.nlm.nih.gov/clinvar/?term={chrom}[CHR]+AND+{pos}[chrpos37]"
    
    clinvar_miner_url = ""
    if "rs" in variant:
        rs = variant["rs"]
        clinvar_miner_url = f"https://clinvarminer.genetics.utah.edu/search?q={rs}"

    html = templates.get_template(
        "card.html.jinja2", 
    ).render(title="Clinvar", text="", subtitle="", links=[{"url": url, "text": "Go"}, {"url": clinvar_miner_url, "text": "Miner"}])

    return SourceResult("Clinvar", {}, html, True)

async def Clinvar_chr_pos_ref_alt(session: aiohttp.ClientSession, variant: dict):
    url = ""
    chrom = variant["chr"]
    pos = variant["pos"]
    ref = variant["ref"]
    alt = variant["alt"]
    url = f"https://www.ncbi.nlm.nih.gov/clinvar/?term={chrom}[CHR]+AND+{pos}[chrpos37]+{ref}>{alt}"
    
    clinvar_miner_url = ""
    if "rs" in variant:
        rs = variant["rs"]
        clinvar_miner_url = f"https://clinvarminer.genetics.utah.edu/search?q={rs}"

    html =  templates.get_template(
        "card.html.jinja2", 
    ).render(title="Clinvar", text="", subtitle="", links=[{"url": url, "text": "Go"}, {"url": clinvar_miner_url, "text": "Miner"}])

    return SourceResult("Clinvar", {}, html, True)

clinvar_entries = {
    ("chr", "pos", "ref", "alt"): Clinvar_chr_pos_ref_alt,
    ("chr", "pos"): Clinvar_chr_pos,
}
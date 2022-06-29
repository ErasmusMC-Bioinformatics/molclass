def OncoKB(variant: dict):
    url = ""
    if "gene" in variant:
        gene = variant["gene"]
        url = f"https://www.oncokb.org/gene/{gene}"

    return f"""
    <a href="{url}">OncoKB</a>
    """
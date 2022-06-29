def dbSNP(variant):
    url = ""
    if "dbSNP" in variant:
        dbSNP = variant["dbSNP"]
        rs = dbSNP["rs"]

        url = f"https://www.ncbi.nlm.nih.gov/snp/{rs}"

    return f"""
    <a href="{url}">dbSNP</a>
    """
def Clinvar_Miner(variant):
    url = ""
    if "dbSNP" in variant:
        dbSNP = variant["dbSNP"]
        rs = dbSNP["rs"]

        url = f"https://clinvarminer.genetics.utah.edu/search?q={rs}"

    return f"""
    <a href="{url}">Clinvar Miner</a>
    """
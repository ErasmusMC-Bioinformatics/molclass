def lovd(variant: dict):
    url = ""
    if "gene" in variant:
        gene = variant["gene"]
        url = f"https://databases.lovd.nl/shared/genes/{gene}"

    return f"""
    <a href="{url}">Leiden Open Variation Database</a>
    """
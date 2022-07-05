def Cosmic(variant: dict, request):
    url = ""
    if "gene" in variant:
        gene = variant["gene"]
        url = f"https://cancer.sanger.ac.uk/cosmic/gene/analysis?ln={gene}"
    
    return f"""
    <a href="{url}">Cosmic</a>
    """
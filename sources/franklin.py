def Franklin(variant: dict) -> str:
    url = ""
    variant_set = set(variant)
    if set(["chr", "pos", "ref", "alt"]).issubset(variant_set):
        chrom = variant["chr"]
        pos = variant["pos"]
        ref = variant["ref"]
        alt = variant["alt"]
        url = f"https://franklin.genoox.com/clinical-db/variant/snp/chr{chrom}-{pos}-{ref}-{alt}"
    
    return f"""
    <a href="{url}">Franklin</a>
    """
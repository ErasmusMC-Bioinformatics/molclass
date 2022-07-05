def Clinvar(variant: dict, request):
    url = ""
    if set(["chr", "pos"]).issubset(set(variant)):
        print(variant)
        chrom = variant["chr"]
        pos = variant["pos"]
        ref = variant["ref"] if "ref" in variant else ""
        alt = variant["alt"] if "alt" in variant else ""
        refalt = f"+{ref}>{alt}" if ref and alt else ""
        url = f"https://www.ncbi.nlm.nih.gov/clinvar/variation/523362/?oq={chrom}[CHR]+AND+{pos}[chrpos37]{refalt}"

    return f"""
    <a href="{url}">Clinvar</a>
    """
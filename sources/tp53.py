from templates import templates

def TP53(variant: dict, request):
    if "gene" not in variant or variant["gene"].strip() != "TP53":
        return None

    if "cdot" not in variant:
        return None

    url = f"https://tp53.isb-cgc.org/results_somatic_mutation_list"

    cdot = variant["cdot"]

    text = f"""
    <form target="_blank" action="{url}" method="post">
        <input name="sm_include_cdna_list" value="c.673-1G>A" type="hidden" />
        <input type="submit" value="Go"  class="btn btn-primary">
    </input>"""

    return templates.get_template(
        "card.html.jinja2", 
    ).render(title="TP53", text=text, subtitle="", links=[])
import asyncio
import inspect
import re
import urllib.parse

from markupsafe import escape

from util import reverse_complement
from .source_result import Source, SourceURL

# the role of a gene in cancer, as shown on the Genome Nexus website. It comes from the OncoKB cancer gene list.
# Each role is shown as a band with a colored bar on the left: (text, color of the bar)
GENE_TYPES = {
    "ONCOGENE": [("Oncogene", "#dc3545")],
    "TSG": [("Tumor suppressor gene", "#0d6efd")],
    "ONCOGENE_AND_TSG": [("Oncogene", "#dc3545"), ("Tumor suppressor gene", "#0d6efd")],
}
GENE_TYPE_OTHER_COLOR = "#9a9d96"

# the colors of the protein domains, the same domain gets the same color
DOMAIN_COLORS = ["#2dcf00", "#ff5353", "#5b5bff", "#ebd61d", "#ba21e0", "#ff9c42", "#ff7dff", "#b9264f", "#baba21", "#c48484"]

# the number of tumors the hotspots of cancerhotspots.org (v2) are based on, Chang et al. 2018 (PMID 29247016)
HOTSPOT_TUMORS = 24592

# SIGNAL (signaldb.org): a tumor type needs at least this many patients to get its own bar
SIGNAL_MIN_PATIENTS = 20

# shown when a source doesn't know the variant
NOT_AVAILABLE = "<span class='text-muted'>NA</span>"

# these rarely change, so only ask for them once
_gene_types: dict[str, str | None] = {}          # gene -> type
_proteins: dict[str, tuple[int, list]] = {}      # transcript -> (length, [(domain name, start, end), ...])
_hotspot_changes: dict[tuple, dict] = {}         # (gene, residue) -> {amino acid change: {tumor type: tumors}}
_oncogenicity: dict[str, dict] = {}              # genomic location -> annotation of OncoKB


# the gene types of OncoKB that are neither of the roles above, these get a gray label: (text, text when hovering)
NOT_LISTED = "NOT_LISTED"
OTHER_GENE_TYPES = {
    "INSUFFICIENT_EVIDENCE": ("Oncogene / tumor suppressor gene: insufficient evidence", "OncoKB has insufficient evidence that it is an oncogene or a tumor suppressor gene"),
    "NEITHER": ("Neither oncogene nor tumor suppressor gene", "according to OncoKB"),
    NOT_LISTED: ("Not listed as oncogene or tumor suppressor gene", "not in the cancer gene list of OncoKB"),
}


def gene_type_html(label: str, color: str, tooltip: str = "") -> str:
    """
    The role of the gene: a band across the card with a colored bar on the left and a pale background of the same color.
    It doesn't look like a button, because it is not a link.
    """
    title = f" title='{escape(tooltip)}'" if tooltip else ""
    return (
        f"<div class='fw-semibold ps-2 py-1 mb-1' style='border-left: 4px solid {color}; background: {color}0f'{title}>"
        f"{escape(label)}</div>"
    )


def link_line(name: str, url: str, value: str) -> str:
    """
    A line of the card with a button to the source and what the source says, like the links of the other cards.
    The buttons have the same width, so the values are below each other.
    """
    return (
        "<div class='d-flex align-items-center gap-2 mb-1 small'>"
        f"<a target='_blank' class='btn btn-primary btn-sm py-0 flex-shrink-0' style='min-width: 7.5rem' href='{escape(url)}'>{escape(name)}</a>"
        f"<span>{value}</span></div>"
    )


def protein_svg(length: int, domains: list, position: int, label: str) -> str:
    """
    Draws the protein with its domains and the variant as a 'lollipop', like the Genome Nexus website does.
    The names of domains that are too small for it are only shown when hovering over them.
    """
    width, left, right = 300, 6, 294

    def x(residue) -> float:
        return left + (right - left) * min(max(residue, 0), length) / length

    names = sorted({name for name, _, _ in domains})
    parts = [f"<rect x='{left}' y='41' width='{right - left}' height='8' fill='#babdb6' />"]
    for name, start, end in sorted(domains, key=lambda domain: domain[1]):
        domain_width = max(x(end) - x(start), 1)
        color = DOMAIN_COLORS[names.index(name) % len(DOMAIN_COLORS)]
        parts.append(
            f"<g><title>{escape(name)} ({start}-{end})</title>"
            f"<rect x='{x(start):.1f}' y='37' width='{domain_width:.1f}' height='16' fill='{color}' />"
        )
        if len(name) * 4.6 < domain_width - 2:
            parts.append(f"<text x='{x(start) + domain_width / 2:.1f}' y='48' font-size='8' text-anchor='middle' fill='#fff'>{escape(name)}</text>")
        parts.append("</g>")

    # keep the label of a variant at the start or end of the protein inside the picture
    anchor = "start" if x(position) < 40 else "end" if x(position) > width - 40 else "middle"
    parts.append(
        f"<line x1='{x(position):.1f}' y1='18' x2='{x(position):.1f}' y2='37' stroke='#babdb6' />"
        f"<circle cx='{x(position):.1f}' cy='16' r='3.5' fill='#000' />"
        f"<text x='{x(position):.1f}' y='9' font-size='9' text-anchor='{anchor}'>{escape(label)}</text>"
        f"<text x='{left}' y='63' font-size='7' fill='#6c757d'>1</text>"
        f"<text x='{right}' y='63' font-size='7' text-anchor='end' fill='#6c757d'>{length} aa</text>"
    )
    return f"<svg viewBox='0 0 {width} 66' width='100%' role='img' aria-label='Position of the variant in the protein'>{''.join(parts)}</svg>"


def bars_svg(rows: list[tuple], description: str, label_width: int, value_width: int) -> str:
    """
    Draws a horizontal bar chart of rows of (name, size of the bar, text behind the bar, text when hovering, is a sum).
    A row that is a sum of the rows that didn't get their own bar is drawn in gray, it is not one group.
    """
    width, row_height, bar_height, radius = 300, 12, 7, 3
    largest = max(size for _, size, _, _, _ in rows) or 1
    parts = []
    for index, (name, size, value, tooltip, is_sum) in enumerate(rows):
        y = index * row_height + 2
        color = "#9a9d96" if is_sum else "#2a78d6"
        bar = max((width - label_width - value_width) * size / largest, 1)
        if bar > radius:  # rounded at the end of the bar, square at the baseline
            shape = (
                f"<path d='M{label_width},{y} h{bar - radius:.1f} a{radius},{radius} 0 0 1 {radius},{radius} "
                f"v{bar_height - 2 * radius} a{radius},{radius} 0 0 1 -{radius},{radius} h-{bar - radius:.1f} z' fill='{color}' />"
            )
        else:
            shape = f"<rect x='{label_width}' y='{y}' width='{bar:.1f}' height='{bar_height}' fill='{color}' />"
        parts.append(
            f"<g><title>{escape(tooltip)}</title>"
            f"<rect x='0' y='{y - 2}' width='{width}' height='{row_height}' fill='transparent' />"
            f"<text x='{label_width - 5}' y='{y + 6.5}' font-size='8' text-anchor='end' fill='#52514e'>{escape(name)}</text>"
            f"{shape}"
            f"<text x='{label_width + bar + 4:.1f}' y='{y + 6.5}' font-size='8' fill='#0b0b0b'>{escape(value)}</text></g>"
        )
    height = len(rows) * row_height + 2
    return f"<svg viewBox='0 0 {width} {height}' width='100%' role='img' aria-label='{escape(description)}'>{''.join(parts)}</svg>"


def tumor_types_svg(tumor_types: dict[str, int], mutation: str) -> str:
    """
    Draws the number of tumors with the mutation ('G12D', or 'a mutation at G12') per tumor type as a bar chart.
    Only the most common tumor types get a bar, the others are added up.
    """
    total = sum(tumor_types.values())
    names = {"unk": "unknown", "head_neck": "head & neck"}
    ranked = [(names.get(name, name.replace("_", " ")).capitalize(), count) for name, count in sorted(tumor_types.items(), key=lambda item: -item[1])]
    shown = ranked if len(ranked) <= 6 else ranked[:5]
    rows = [
        (name, count, str(count), f"{name}: {count} of the {total} tumors with {mutation} ({100 * count / total:.0f}%)", False)
        for name, count in shown
    ]
    if len(ranked) > len(shown):
        others = sum(count for _, count in ranked[5:])
        name = f"Other ({len(ranked) - 5} types)"
        rows.append((name, others, str(others), f"{name}: {others} of the {total} tumors with {mutation} ({100 * others / total:.0f}%)", True))
    return bars_svg(rows, f"Tumors with {mutation} per tumor type", 78, 34)


def signal_svg(counts: list[dict], status: str) -> str:
    """
    Draws in which share of the patients of a tumor type the variant was found, for the tumor types where that is highest.
    A tumor type with only a few patients easily gets a high share, so those don't get their own bar.
    """
    found = [(c["tumorType"], c["variantCount"], c["tumorTypeCount"]) for c in counts if c.get("variantCount") and c.get("tumorTypeCount")]
    ranked = sorted([c for c in found if c[2] >= SIGNAL_MIN_PATIENTS], key=lambda c: -c[1] / c[2])
    shown = ranked if len(ranked) <= 6 else ranked[:5]
    others = [c for c in found if c not in shown]

    def row(name, variants, patients, is_sum):
        share = f"{100 * variants / patients:.2g}%"
        label = name if len(name) <= 28 else name[:27] + "…"
        tooltip = f"{name}: {status} in {variants} of the {patients} patients ({share})"
        return (label, variants / patients, f"{share} ({variants}/{patients})", tooltip, is_sum)

    rows = [row(*c, False) for c in shown]
    if others:
        rows.append(row(f"Other ({len(others)} types)", sum(c[1] for c in others), sum(c[2] for c in others), True))
    return bars_svg(rows, f"Share of the patients with the variant ({status}) per tumor type", 124, 62)


class GenomeNexus(Source):
    def set_entries(self):
        self.entries = {
            ("transcript", "cdot"): self.transcript_cdot,
            ("chr", "pos", "ref", "alt"): self.chr_pos_ref_alt
        }

    async def get_annotation(self, query) -> dict:
        enc_query = urllib.parse.quote(query)
        api_url = f"https://www.genomenexus.org/annotation/{enc_query}?fields=annotation_summary,hotspots,my_variant_info,signal,clinvar"
        resp, json = await self.async_get_json(api_url)
        return json if isinstance(json, dict) else {}

    async def check_validity(self, query):
        return (await self.get_annotation(query)).get("successfully_annotated", False)

    async def get_gene_type(self, gene: str) -> str | None:
        if gene not in _gene_types:
            url = f"https://public.api.oncokb.org/api/v1/genes/lookup?query={urllib.parse.quote(gene)}"
            _, genes = await self.async_get_json(url)
            if not isinstance(genes, list):
                return None
            # the lookup also returns genes that have the query as an alias
            types = [g.get("geneType") for g in genes if isinstance(g, dict) and g.get("hugoSymbol") == gene]
            _gene_types[gene] = types[0] if types else NOT_LISTED
        return _gene_types[gene]

    async def get_protein(self, transcript: str) -> tuple[int, list] | None:
        """Returns the length of the protein of the (ensembl) transcript and its pfam domains as (name, start, end)"""
        if transcript not in _proteins:
            _, info = await self.async_get_json(f"https://www.genomenexus.org/ensembl/transcript/{urllib.parse.quote(transcript)}")
            if not isinstance(info, dict) or not info.get("proteinLength"):
                return None

            # a protein without domains can have a list with one empty domain
            domains = [domain for domain in info.get("pfamDomains") or [] if domain.get("pfamDomainId")]
            names = {}
            if domains:
                ids = sorted({domain["pfamDomainId"] for domain in domains})
                _, pfam = await self.async_post_json("https://www.genomenexus.org/pfam/domain", json=ids)
                names = {domain["pfamAccession"]: domain["name"] for domain in pfam} if isinstance(pfam, list) else {}
            _proteins[transcript] = (
                int(info["proteinLength"]),
                [(names.get(d["pfamDomainId"], d["pfamDomainId"]), int(d["pfamDomainStart"]), int(d["pfamDomainEnd"])) for d in domains],
            )
        return _proteins[transcript]

    def get_hotspots(self, annotation: dict) -> dict[str, int]:
        """
        Returns the hotspots (cancerhotspots.org) the variant is in, with the number of tumors they were seen in.
        There is a list of hotspots for every transcript, and a hotspot can be in there
        more than once (as 'single residue' and as '3d' hotspot), the highest count is used.
        """
        counts: dict[str, int] = {}
        for hotspots in (annotation.get("hotspots") or {}).get("annotation") or []:
            for hotspot in hotspots or []:
                residue = hotspot.get("residue")
                if residue:
                    counts[residue] = max(counts.get(residue, 0), hotspot.get("tumorCount") or 0)
        return counts

    def get_summary(self, annotation: dict) -> dict:
        """
        Returns the consequences of the variant for the transcript that was searched for, so the exon
        and protein position are the ones the user expects. Genome Nexus uses ensembl transcripts,
        if none of them belongs to the searched transcript its own choice for the gene is returned.
        """
        annotation_summary = annotation.get("annotation_summary") or {}
        default = annotation_summary.get("transcriptConsequenceSummary") or {}

        searched = str(self.variant.get("transcript") or "").split(".")[0].upper()
        ensembl_ids = {
            consequence.get("transcript_id")
            for consequence in annotation.get("transcript_consequences") or []
            if searched in [str(refseq).split(".")[0].upper() for refseq in consequence.get("refseq_transcript_ids") or []]
        }
        if not searched or default.get("transcriptId") in ensembl_ids:
            return default
        for summary in annotation_summary.get("transcriptConsequenceSummaries") or []:
            if summary.get("transcriptId") in ensembl_ids:
                return summary
        return default

    async def get_hotspot_changes(self, gene: str, residue: str) -> dict[str, dict]:
        """
        Returns the amino acid changes that were seen at the hotspot, as {change: {tumor type: tumors}},
        directly from cancerhotspots.org. Genome Nexus only has the number of tumors for the whole hotspot.
        All hotspots are retrieved at once, the first time one is needed.
        """
        if not _hotspot_changes:
            _, variants = await self.async_get_json("https://www.cancerhotspots.org/api/variants")
            if not isinstance(variants, list):
                return {}
            for variant in variants:
                key = (variant.get("hugoSymbol"), variant.get("residue"))
                _hotspot_changes.setdefault(key, {})[variant.get("variantAminoAcid")] = variant.get("tumorTypeComposition") or {}
        return _hotspot_changes.get((gene, residue), {})

    def get_clinvar(self, annotation: dict) -> str:
        """Returns the html for the interpretation of the variant in ClinVar, NA if ClinVar doesn't have it"""
        clinvar = (annotation.get("clinvar") or {}).get("annotation") or {}
        significance = str(clinvar.get("clinicalSignificance") or "").replace("_", " ")
        if not significance or not clinvar.get("clinvarId"):
            return link_line("ClinVar", "https://www.ncbi.nlm.nih.gov/clinvar/", NOT_AVAILABLE)
        # for conflicting classifications: Pathogenic(1)|Uncertain_significance(1)
        conflicting = str(clinvar.get("conflictingClinicalSignificance") or "").replace("_", " ").replace("|", ", ")
        url = f"https://www.ncbi.nlm.nih.gov/clinvar/variation/{urllib.parse.quote(str(clinvar['clinvarId']))}/"
        return link_line("ClinVar", url, f"<b>{escape(significance)}</b>" + (f" ({escape(conflicting)})" if conflicting else ""))

    async def get_oncokb(self, annotation: dict) -> str:
        """
        Returns the html for the effect of the variant according to OncoKB (Oncogenic, Gain-of-function),
        NA if OncoKB doesn't know. This is what OncoKB makes public, the treatments need a license (see the OncoKB source).
        """
        unknown = link_line("OncoKB", "https://www.oncokb.org/", NOT_AVAILABLE)
        ref, _, alt = str(annotation.get("allele_string") or "").partition("/")
        location = f"{annotation.get('seq_region_name')},{annotation.get('start')},{annotation.get('end')},{ref},{alt}"
        if not ref or not alt or "None" in location:
            return unknown

        if location not in _oncogenicity:
            url = (
                "https://public.api.oncokb.org/api/v1/annotate/mutations/byGenomicChange"
                f"?genomicLocation={urllib.parse.quote(location)}&referenceGenome=GRCh37"
            )
            _, oncokb = await self.async_get_json(url)
            if not isinstance(oncokb, dict) or "oncogenic" not in oncokb:
                return unknown
            if len(_oncogenicity) >= 1000:
                _oncogenicity.clear()
            _oncogenicity[location] = oncokb

        oncokb = _oncogenicity[location]
        effects = [oncokb.get("oncogenic"), (oncokb.get("mutationEffect") or {}).get("knownEffect")]
        effects = [effect for effect in effects if effect and effect != "Unknown"]

        query = oncokb.get("query") or {}
        url = "https://www.oncokb.org/"
        if query.get("hugoSymbol") and oncokb.get("geneExist"):
            url += f"gene/{urllib.parse.quote(str(query['hugoSymbol']))}"
            # OncoKB has a page for every variant of a gene it has, also when the variant is only
            # classified by a rule (truncating mutations of BRCA1), like the link on the Genome Nexus website.
            # A variant outside the protein gets an alteration like *30*, that has no page
            if re.fullmatch(r"[A-Z]\d+.*", str(query.get("alteration") or "")):
                url += f"/{urllib.parse.quote(str(query['alteration']))}"
        effect = f"<b>{escape(', '.join(effects))}</b>" if effects else NOT_AVAILABLE
        return link_line("OncoKB", url, effect)

    async def get_hotspot_section(self, annotation: dict, summary: dict, gene: str | None, with_chart: bool) -> str:
        """
        Returns the html that tells if the variant is a hotspot of cancerhotspots.org, and in which tumor types
        """
        hotspots = self.get_hotspots(annotation)
        url = "https://www.cancerhotspots.org/"
        lines, charts = [], ""
        for residue, count in hotspots.items():
            changes = await self.get_hotspot_changes(gene, residue) if gene else {}
            tooltip = f"Any mutation at {residue}: {count} of the {HOTSPOT_TUMORS} tumors (all cancer types) of cancerhotspots.org"
            if changes:
                common = sorted(changes.items(), key=lambda item: -sum(item[1].values()))[:5]
                tooltip += ". Changes: " + ", ".join(f"{change} ({sum(tumor_types.values())})" for change, tumor_types in common)

            # the hotspot is a position (G12), the tumor types are shown for the exact change (G12D) when it was seen.
            # A substitution is listed by its new amino acid (D), a deletion/insertion in full (E746_A750del).
            protein_change = str(summary.get("hgvspShort") or "").removeprefix("p.")
            tumor_types = changes.get(protein_change.removeprefix(residue)) or changes.get(protein_change)
            if tumor_types:
                exact = sum(tumor_types.values())
                label = f"{protein_change} ({100 * exact / HOTSPOT_TUMORS:.2g}% of tumors)"
                tooltip = f"{protein_change}: {exact} tumors. {tooltip}"
                charts += tumor_types_svg(tumor_types, protein_change)
            else:
                label = f"{residue} ({100 * count / HOTSPOT_TUMORS:.2g}% of tumors)"
                if changes:
                    label += f", {protein_change or 'this change'} itself not listed"
                    everything: dict[str, int] = {}
                    for tumor_types in changes.values():
                        for tumor_type, tumors in tumor_types.items():
                            everything[tumor_type] = everything.get(tumor_type, 0) + tumors
                    charts += tumor_types_svg(everything, f"a mutation at {residue}")
            lines.append(link_line("Cancer hotspots", url, f"<b title='{escape(tooltip)}'>{escape(label)}</b>"))

        # say so when it is not a hotspot, otherwise it looks the same as when the hotspots could not be retrieved
        if not hotspots and isinstance((annotation.get("hotspots") or {}).get("annotation"), list):
            lines.append(link_line("Cancer hotspots", url, "<span class='text-muted'>Not a hotspot</span>"))
        if not lines:
            return ""
        return f"{''.join(lines)}{charts if with_chart else ''}"

    def get_signal(self, annotation: dict, query: str) -> str:
        """
        Returns the html for how often the variant was found, somatic and/or germline, in the patients of SIGNAL
        (signaldb.org), these had their tumor and blood sequenced with MSK-IMPACT. Empty if SIGNAL doesn't have the variant.
        """
        text = ""
        url = f"https://www.signaldb.org/variant/{urllib.parse.quote(query.removeprefix('chr'), safe=':>')}"
        for signal in (annotation.get("signalAnnotation") or {}).get("annotation") or []:
            counts = signal.get("countsByTumorType") or []
            patients = sum(count.get("tumorTypeCount") or 0 for count in counts)
            variants = sum(count.get("variantCount") or 0 for count in counts)
            status = signal.get("mutationStatus") or "found"
            if not patients or not variants:
                continue

            tooltip = f"{status.capitalize()} in {variants} of the {patients} patients (all tumor types) of signaldb.org"
            extra = []
            if status == "germline" and signal.get("penetrance"):
                extra.append(f"{str(signal['penetrance']).lower()} penetrance")
            if status == "germline" and signal.get("mskExperReview"):
                extra.append("reviewed by MSK experts")
            text += (
                link_line(
                    "SIGNAL", url,
                    f"<b title='{escape(tooltip)}'>{escape(status)} in {100 * variants / patients:.2g}% of patients</b>"
                    f"{escape(', ' + ', '.join(extra)) if extra else ''}",
                )
                + signal_svg(counts, status)
            )
        return text

    async def attempt(self, section: str, function, *args, default=None, **kwargs):
        """
        Returns the result of the (async) function, or the default when it fails. The details of the card
        come from several places, when one of them fails the others are still shown and the failure is logged.
        """
        try:
            result = function(*args, **kwargs)
            return await result if inspect.isawaitable(result) else result
        except Exception as e:
            self.log_warning(f"Could not get the {section}: {type(e).__name__}: {e}")
            return default

    async def add_details(self, query):
        """
        Shows if the gene of the variant is an oncogene and/or tumor suppressor gene, the exon and protein domain,
        where the variant is in the protein, if it is a cancer hotspot, how often it is found per tumor type
        and a link to COSMIC.
        This is extra information, so the card is not failed if it can't be retrieved.
        """
        text = ""
        annotation = await self.attempt("annotation", self.get_annotation, query, default={})
        summary = await self.attempt("transcript of the annotation", self.get_summary, annotation, default={})

        gene = summary.get("hugoGeneSymbol")
        gene_type = await self.attempt("gene type", self.get_gene_type, gene) if gene else None
        if gene_type in GENE_TYPES:
            labels = "".join(gene_type_html(label, color) for label, color in GENE_TYPES[gene_type])
            text += f"<div class='mb-2'>{labels}</div>"
            self.html_text = text
        elif gene_type:
            # say so when it is neither, otherwise it looks the same as when the role of the gene could not be retrieved
            label, reason = OTHER_GENE_TYPES.get(gene_type, (str(gene_type).replace("_", " ").capitalize(), "gene type of OncoKB"))
            text += f"<div class='mb-2'>{gene_type_html(label, GENE_TYPE_OTHER_COLOR, f'{gene}: {reason}')}</div>"
            self.html_text = text

        # variants outside the coding sequence don't have a position in the protein
        position = (summary.get("proteinPosition") or {}).get("start")
        transcript = summary.get("transcriptId")
        protein = await self.attempt("protein", self.get_protein, transcript) if position and transcript else None

        if protein:
            length, domains = protein
            text += await self.attempt("protein diagram", protein_svg, length, domains, int(position), summary.get("hgvspShort") or str(position), default="")
            self.html_text = text

        details = []
        if summary.get("exon"):
            details.append(f"Exon {escape(str(summary['exon']).split('/')[0])}")
        if protein:
            details += [f"{escape(name)} domain" for name, start, end in protein[1] if start <= int(position) <= end]
        if details:
            text += f"<p class='small mb-1'>{' &middot; '.join(dict.fromkeys(details))}</p>"

        pathogenicity = [
            await self.attempt("ClinVar interpretation", self.get_clinvar, annotation),
            await self.attempt("OncoKB interpretation", self.get_oncokb, annotation),
        ]
        pathogenicity = [line for line in pathogenicity if line]
        # a line between the sections: the position in the gene, the interpretation and how often it is found
        if pathogenicity:
            text += f"<div class='mt-2 mb-2 pt-2 border-top'>{''.join(pathogenicity)}</div>"
            self.html_text = text

        # SIGNAL has the share of the patients per tumor type, that says more than the number of tumors
        # of the hotspot. So the tumor types of the hotspot are only drawn when SIGNAL doesn't have the variant.
        signal = await self.attempt("SIGNAL frequencies", self.get_signal, annotation, query, default="")
        hotspot = await self.attempt("cancer hotspot", self.get_hotspot_section, annotation, summary, gene, with_chart=not signal, default="")
        if hotspot or signal:
            text += f"<div class='mt-2 pt-2 border-top'>{hotspot}{signal}</div>"
        self.html_text = text

        cosmic = ((annotation.get("my_variant_info") or {}).get("annotation") or {}).get("cosmic") or {}
        if isinstance(cosmic, dict) and cosmic.get("cosmicId"):
            cosmic_id = urllib.parse.quote(str(cosmic["cosmicId"]))
            self.shared_links["COSMIC"] = SourceURL(f"COSMIC {cosmic_id}", f"https://cancer.sanger.ac.uk/cosmic/search?genome=37&q={cosmic_id}")
        # a timeout of one of the requests is not a timeout of the card
        self.timeout = False

    async def chr_pos_ref_alt(self):
        """
        Simply add a URL to the variant, won't work for more del, ins, dup, etc.
        Probably could add support for those, but would take other fields then pos, ref, alt.
        """
        chrom = self.variant["chr"]
        pos = self.variant["pos"]
        ref = self.variant["ref"]
        alt = self.variant["alt"]
        if not ref or not alt:
            self.found = False
            return

        # Check if annotation exists for ref/alt, if not try the reverse complement
        if not await self.check_validity(f"{chrom}:g.{pos}{ref}>{alt}"):
            ref = reverse_complement(ref)
            alt = reverse_complement(alt)
            if not await self.check_validity(f"{chrom}:g.{pos}{ref}>{alt}"):
                self.html_text = (f"No annotation found for either {chrom}:g.{pos}{self.variant['ref']}>{self.variant['alt']} "
                                  f"or {chrom}:g.{pos}{ref}>{alt} (reverse complement).")
                self.found = False
                return

        url = f"https://www.genomenexus.org/variant/{chrom}:g.{pos}{ref}>{alt}"
        self.html_title = ""  # the name is on the link at the bottom of the card
        self.html_links["main"] = SourceURL("Genome Nexus", url)
        await self.add_details(f"{chrom}:g.{pos}{ref}>{alt}")

    async def transcript_cdot(self):
        """
        Link to the variant by its genomic (hgvs) notation
        """
        # Genome Nexus is hg19, the hg38 position is only looked up to show it at the top of the page
        resolved, _ = await asyncio.gather(self.resolve_coordinates(), self.resolve_gdot(build="GRCh38"))
        if resolved is None:
            self.found = False
            return

        url = f"https://www.genomenexus.org/variant/{resolved.gdot}"
        self.html_title = ""  # the name is on the link at the bottom of the card
        self.html_links["main"] = SourceURL("Genome Nexus", url)
        await self.add_details(resolved.gdot)
        self.complete = True

    def get_name(self):
        return "Genome Nexus"
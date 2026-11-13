import asyncio
import math
import urllib.parse

import numpy as np
from pydantic_settings import BaseSettings

from .source_result import Source, SourceURL

# AlphaGenome's client is synchronous (not aiohttp-based), so calls to it are
# wrapped in asyncio.to_thread() to avoid blocking the event loop.
try:
    from alphagenome.atlas import atlas
    from alphagenome.data import genome
except ImportError:
    # without the package only this source is not available, the rest of Molclass still works
    atlas = genome = None

ATLAS_BROWSER_URL = "https://deepmind.google.com/science/alphagenome/atlas"

# Display names for the AVI score's 18 biological modality features
# https://github.com/google-deepmind/science-skills/blob/main/skills/alphagenome_variant_impact_score/scripts/alphagenome_atlas_avi.py
FEATURE_DISPLAY_NAMES = {
    "MERGED_SPLICING": "Splicing",
    "MAX_ABS_RNA_SEQ": "RNA-seq",
    "MAX_ABS_ATAC": "ATAC-seq",
    "MAX_ABS_DNASE": "DNase-seq",
    "MAX_ABS_CHIP_TF": "ChIP-TF",
    "MAX_ABS_CHIP_HISTONE": "ChIP-Histone",
    "MAX_ABS_CAGE": "CAGE",
    "MAX_ABS_PROCAP": "PRO-cap",
    "MAX_ABS_POLYADENYLATION": "Polyadenylation",
    "MAX_ABS_CONTACT_MAPS": "3D Genome Contacts",
    "ALPHAMISSENSE": "AlphaMissense",
    "CACTUS_241_WAY": "Cactus",
    "PROTEIN_TERMINATION": "Protein Termination",
    "START_LOST": "Start Lost",
    "STOP_LOST": "Stop Lost",
    "PHASTCONS_470_WAY": "PhastCons 470",
    "IS_INSERTION": "Insertion",
    "IS_DELETION": "Deletion",
}


# the number of features to show of the 18 the score is based on
FEATURES_SHOWN = 4


def _features_html(rows: list[tuple]) -> str:
    """
    Draws rows of (name of the feature, weight) as bars relative to the largest weight.
    This is not a svg, because the names have to stay readable in a narrow card.
    """
    largest = max(abs(value) for _, value in rows)
    cells = []
    for name, value in rows:
        direction = "raises" if value > 0 else "lowers"
        color = "#2a78d6" if value > 0 else "#eb6834"
        title = f"title='{name} {direction} the score: {value:+.4f}'"
        cells.append(
            f"<span {title} style='color: #52514e'>{name}</span>"
            f"<span {title}><span style='display: block; height: 8px; min-width: 2px; border-radius: 0 4px 4px 0; "
            f"width: {100 * abs(value) / largest:.0f}%; background: {color}'></span></span>"
            f"<span {title}>{value:+.2f}</span>"
        )
    return (
        "<div class='border-top mt-2 pt-2' role='img' aria-label='The features that contribute most to the AlphaGenome score' "
        "style='display: grid; grid-template-columns: auto 1fr auto; column-gap: 6px; align-items: center; "
        f"font-size: 0.7rem; line-height: 1.35'>{''.join(cells)}</div>"
    )


class Secrets(BaseSettings):
    alphagenome_api_key: str | None = None


secrets = Secrets()

# AVI_QUANTILE (the tail) is defined as 1 - CDF, and applying any distribution's
# own CDF to itself always yields exactly Uniform(0, 1) (probability integral
# transform) -- this is how the Atlas's calibration is built, not an assumption
# made here. Since Phred = -10*log10(tail), the background Phred distribution
# across all genome-wide SNVs is therefore exactly Exponential(rate=EXP_RATE),
# in closed form -- no access to Atlas's internal calibration sample is needed
# to draw it.
EXP_RATE = math.log(10) / 10


def _phred_distribution_svg(phred_score: float, top_percentile: float) -> str:
    """
    Renders the background Phred-score distribution (exact Exponential curve,
    see EXP_RATE above) as an inline SVG, with a marker at this variant's score
    and the tail area (== top_percentile) shaded.
    """
    width, height = 280, 118
    pad_left, pad_right, pad_top, pad_bottom = 8, 8, 26, 20
    plot_w = width - pad_left - pad_right
    plot_h = height - pad_top - pad_bottom

    domain_max = max(50.0, phred_score * 1.25)
    n_points = 60

    def x_px(p):
        return pad_left + (p / domain_max) * plot_w

    def density(p):
        return EXP_RATE * math.exp(-EXP_RATE * p)

    peak = density(0.0)

    def y_px(d):
        return pad_top + plot_h - (d / peak) * plot_h

    points = [(x_px(domain_max * i / n_points), y_px(density(domain_max * i / n_points)))
              for i in range(n_points + 1)]
    curve_path = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in points)

    shaded_points = [(x, y) for x, y in points if x >= x_px(phred_score)]
    if shaded_points:
        baseline_y = pad_top + plot_h
        shade_path = (
            f"M{x_px(phred_score):.1f},{baseline_y:.1f} "
            + " L".join(f"{x:.1f},{y:.1f}" for x, y in shaded_points)
            + f" L{width - pad_right:.1f},{baseline_y:.1f} Z"
        )
    else:
        shade_path = ""

    marker_x = x_px(min(phred_score, domain_max))
    if marker_x > width - 55:
        anchor, label_x = "end", min(marker_x, width - pad_right)
    elif marker_x < 55:
        anchor, label_x = "start", max(marker_x, pad_left)
    else:
        anchor, label_x = "middle", marker_x

    return f"""
<svg viewBox="0 0 {width} {height}" width="100%" height="{height}" role="img" aria-label="Background Phred score distribution">
  <path d="{shade_path}" fill="#dc3545" fill-opacity="0.25" stroke="none"></path>
  <path d="{curve_path}" fill="none" stroke="#6c757d" stroke-width="1.5"></path>
  <line x1="{marker_x:.1f}" y1="{pad_top}" x2="{marker_x:.1f}" y2="{pad_top + plot_h:.1f}" stroke="#dc3545" stroke-width="1.5" stroke-dasharray="3,2"></line>
  <circle cx="{marker_x:.1f}" cy="{y_px(density(phred_score)):.1f}" r="3" fill="#dc3545"></circle>
  <text x="{label_x:.1f}" y="20" font-size="15" text-anchor="{anchor}" fill="#dc3545"><tspan font-weight="700">top {top_percentile:.4g}%</tspan> ({phred_score:.1f})</text>
  <text x="{pad_left}" y="{height - 4}" font-size="8" fill="#6c757d">0</text>
  <text x="{width - pad_right}" y="{height - 4}" font-size="8" text-anchor="end" fill="#6c757d">{domain_max:.0f} Phred</text>
</svg>
""".strip()


class AlphaGenome(Source):
    _client = None

    def set_entries(self):
        self.entries = {
            ("transcript", "cdot"): self.transcript_cdot,
        }

    def is_complete(self) -> bool:
        if atlas is None:
            print("Need the alphagenome package for AlphaGenome")
            return False
        if not secrets.alphagenome_api_key:
            print("Need ALPHAGENOME_API_KEY env variable for AlphaGenome")
            return False
        return True

    @classmethod
    def get_client(cls):
        if cls._client is None:
            cls._client = atlas.create(secrets.alphagenome_api_key)
        return cls._client

    async def transcript_cdot(self):
        """
        Looks up the precomputed AlphaGenome Variant Impact (AVI) score of the variant in the AlphaGenome Atlas.
        AlphaGenome only supports GRCh38, so the hg38 genomic coordinates of the transcript:cdot are used.
        """
        resolved = await self.resolve_coordinates(build="GRCh38")
        if resolved is None:
            self.html_text = "Could not determine the hg38 position of this variant."
            self.found = False
            self.complete = True
            return

        chrom, pos, ref, alt = resolved.chr, resolved.pos, resolved.ref, resolved.alt

        # the Atlas answers 'Reference or alternate bases length > 1 not yet supported' for anything else
        if len(ref) != 1 or len(alt) != 1:
            self.html_text = "AlphaGenome only has scores for substitutions of a single base."
            self.found = False
            self.complete = True
            return

        def _query_avi():
            # Everything alphagenome-related (client creation, Variant construction,
            # query_variant) runs inside this thread, never touching the event loop
            # directly: if any of it blocks (network call, lazy model/config load),
            # it would freeze every other source's asyncio.gather() in router.py too.
            client = self.get_client()
            variant = genome.Variant(
                chromosome=f"chr{chrom}",
                position=pos,
                reference_bases=ref,
                alternate_bases=alt,
            )
            return client.query_variant(
                variant, requested_scorers=["AVI_SCORE", "AVI_SCORE_FEATURE_IMPORTANCE"]
            )

        try:
            scores = await asyncio.wait_for(asyncio.to_thread(_query_avi), timeout=30)
        except asyncio.TimeoutError:
            # query_variant runs in a thread outside aiohttp's timeout handling,
            # so it needs its own timeout or a hung/slow call blocks every other
            # source's asyncio.gather() in router.py too.
            raise TimeoutError()
        except Exception as exc:
            # AlphaGenome rejects variants whose hg38 reference base differs from the
            # sequence (common after hg19 liftover); report that instead of a traceback.
            if "reference base" in str(exc).lower():
                self.html_text = "hg38 reference base mismatch, AlphaGenome cannot score this variant"
                self.found = False
                self.complete = True
                return
            raise

        avi_adata = scores.get("AVI_SCORE")
        if avi_adata is None or avi_adata.X is None or avi_adata.X.size == 0:
            self.found = False
            self.complete = True
            return

        raw_score = float(np.ravel(avi_adata.X)[0])
        phred_score = None
        top_percentile = None
        if "quantiles" in avi_adata.layers:
            cdf_quantile = float(np.ravel(avi_adata.layers["quantiles"])[0])
            # Same conversion the Atlas website itself uses: phred = -10*log10(tail)
            tail = max(1e-7, 1.0 - cdf_quantile)
            phred_score = -10.0 * math.log10(tail)
            top_percentile = tail * 100.0

        # Distribution of the 18 biological modality feature importances (SHAP-like
        # attribution weights) that make up the AVI score, sorted by magnitude.
        feature_rows = []
        fi_adata = scores.get("AVI_SCORE_FEATURE_IMPORTANCE")
        if fi_adata is not None and fi_adata.X is not None and fi_adata.X.size > 0:
            values = np.ravel(fi_adata.X)
            if "name" in getattr(fi_adata, "var", {}):
                names = list(fi_adata.var["name"])
            else:
                names = list(fi_adata.var_names)
            feature_rows = sorted(zip(names, values), key=lambda nv: abs(nv[1]), reverse=True)

        variant_id = f"chr{chrom}:{pos}:{ref}>{alt}"
        atlas_url = f"{ATLAS_BROWSER_URL}?q={urllib.parse.quote(variant_id)}&m=variant"

        text_parts = []
        if phred_score is not None:
            text_parts.append(_phred_distribution_svg(phred_score, top_percentile))
        else:
            text_parts.append(f"<div>Raw AVI score: {raw_score:.4f}</div>")

        if feature_rows:
            # what the score is based on, like the breakdown of the AlphaGenome skill:
            # the features with the largest weight, as bars relative to the largest
            rows = [(FEATURE_DISPLAY_NAMES.get(name, name), float(value)) for name, value in feature_rows[:FEATURES_SHOWN]]
            rows = [(name, value) for name, value in rows if round(value, 2) != 0]
            if rows:
                text_parts.append(_features_html(rows))

        self.html_text = "".join(text_parts)
        # the name is on the link at the bottom of the card, the hg38 position is at the top of the page
        self.html_title = ""
        self.html_links["main"] = SourceURL(self.get_name(), atlas_url)
        # the conditions of the AlphaGenome API don't allow clinical use
        self.html_links["note"] = SourceURL("", "", override="<span class='ms-1 align-middle text-nowrap' style='font-size: 0.75em' title='Predicted molecular impact, for research use only.'>For research use only</span>")
        self.complete = True

    def get_name(self):
        return "AlphaGenome"

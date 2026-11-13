import os
from collections import Counter

from jinja2 import BaseLoader, Environment
from markupsafe import escape
from pydantic_settings import BaseSettings

import coordinates
from inhouse_db import lookup, match, normalize_alleles, normalize_chr

from .source_result import Source, SourceURL

TEMPLATE = """
<table class='table table-sm mb-0 fs-6'>
    {% for center in centers %}
    {% for line in center.lines %}
    <tr>
        {% if loop.first %}<td rowspan='{{ center.lines|length }}'>{{ center.name }}</td>{% endif %}
        <td class='{{ line.style }}'>
            {% if line.check %}<small>Possible match, check {{ line.check }}:</small><br />{% endif %}
            {{ line.text }}
        </td>
    </tr>
    {% endfor %}
    {% endfor %}
</table>
"""

# green for benign, yellow for VUS and red for pathogenic
CLASSIFICATION_STYLES = {
    "benign": "table-success",
    "likely benign": "table-success",
    "vus": "table-warning",
    "likely pathogenic": "table-danger",
    "pathogenic": "table-danger",
}

# how far around the variant to look, the same deletion/insertion can be written at several positions in a repeat
WINDOW = 100


class Secrets(BaseSettings):
    inhouse_database: str = "databases/inhouse.db"


secrets = Secrets()


class InHouse(Source):
    def set_entries(self):
        self.entries = {
            ("transcript", "cdot"): self.transcript_cdot,
            ("chr", "pos", "ref", "alt"): self.chr_pos_ref_alt,
        }

    def is_complete(self) -> bool:
        if not os.path.exists(secrets.inhouse_database):
            print("Could not find in-house classification database:", secrets.inhouse_database)
            return False
        return True

    async def transcript_cdot(self):
        """
        Uses the hg19 genomic coordinates of the transcript:cdot, the centers don't all report (the same) transcript
        """
        resolved = await self.resolve_coordinates()
        if resolved is None:
            self.html_text = "Could not determine the hg19 position of this variant."
            self.found = False
            self.complete = True
            return

        await self.report(resolved.chr, resolved.pos, resolved.ref, resolved.alt)

    async def chr_pos_ref_alt(self):
        """For searches by position, these are expected to be hg19 and on the forward strand"""
        await self.report(self.variant["chr"], self.variant["pos"], self.variant["ref"], self.variant["alt"])

    async def report(self, chrom, pos, ref, alt):
        """
        Looks up the genomic variant, see inhouse_db.py for how variants are compared
        """
        self.complete = True
        chrom = normalize_chr(chrom)
        query = normalize_alleles(pos, ref, alt)
        if query is None:
            self.log_warning(f"Not a usable variant: {chrom}:{pos} {ref}>{alt}")
            self.html_text = "Could not determine the hg19 position of this variant."
            self.found = False
            return
        pos, ref, alt = query
        self.log_info(f"Looking up {chrom}:{pos} {ref or '-'}>{alt or '-'} (hg19)")

        center_names, rows, built = lookup(secrets.inhouse_database, chrom, pos - WINDOW, pos + WINDOW)
        # the name and the date of the database are at the bottom of the card, there is nothing to link to
        name = f"{self.get_name()} (database of {built})" if built else self.get_name()
        self.html_title = ""
        # sized like the link buttons of the other sources, so the bottom of the cards in a row is the same height
        label = f"<span class='btn btn-sm my-1 px-0 border-0 disabled text-muted text-start opacity-100'>{escape(name)}</span>"
        self.html_links["main"] = SourceURL("", "", override=label)

        # only a deletion/insertion can be written in more than one way, and only those need the reference
        sequence = None
        sequence_start = pos - WINDOW - 1
        if not (ref and alt) and any(row[1:4] != query and not (row[2] and row[3]) for row in rows):
            longest = max(len(ref), len(alt), *(len(row[2]) for row in rows))
            sequence = await coordinates.reference(self.session, chrom, sequence_start, pos + WINDOW + longest)
            if sequence is None:
                self.log_warning("Could not get the reference sequence, deletions/insertions are compared less precise")

        centers = []
        for name in center_names:
            exact, possible = [], []
            for center, row_pos, row_ref, row_alt, classification in rows:
                if center != name:
                    continue
                result = match((row_pos, row_ref, row_alt), query, sequence, sequence_start)
                if result == "exact":
                    exact.append(classification)
                elif result == "possible":
                    possible.append((f"{chrom}:{row_pos} {row_ref or '-'}>{row_alt or '-'}", classification))

            # one colored line per classification, a center can have more than one for the same variant
            lines = []
            for classification, count in Counter(exact).most_common():
                text = f"{classification} ({count}x)" if count > 1 else classification
                lines.append({"text": text, "style": CLASSIFICATION_STYLES.get(classification.lower(), "")})
            for description, classification in sorted(set(possible)):
                style = CLASSIFICATION_STYLES.get(classification.lower(), "")
                lines.append({"text": classification, "style": style, "check": description})
            if not lines:
                lines.append({"text": "Not found", "style": "table-secondary"})
            centers.append({"name": name, "lines": lines, "found": bool(exact or possible)})

        self.found = any(center["found"] for center in centers)
        template = Environment(loader=BaseLoader(), autoescape=True).from_string(TEMPLATE)
        self.html_text = template.render(centers=centers)

    def get_name(self):
        return "Previously classified"

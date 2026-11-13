import os

import yaml
from jinja2 import BaseLoader, Environment
from pydantic_settings import BaseSettings

from .source_result import HIGHLIGHT, Source

# this source is a banner over the full width of the page, so it has its own, compact, layout instead of the card
TEMPLATE = """
<div class='card {{ highlight }}'>
    <div class='card-body py-2'>
        {% if gene.remark %}<div class='small'>{{ gene.remark }}</div>{% endif %}
        <table class='table table-sm table-borderless mb-0 fs-6'>
            <tr class='border-bottom'>
                <th class='w-50 py-0' title='{{ table.columns.report }}'>PA-verslag</th>
                <th class='w-50 py-0' title='{{ table.columns.mtb }}'>MTB</th>
            </tr>
            <tr>
                <td class='text-break pb-0' style='white-space: pre-line'>{{ gene.report or '-' }}</td>
                <td class='text-break pb-0' style='white-space: pre-line'>{{ gene.mtb or '-' }}</td>
            </tr>
        </table>
    </div>
    <div class='card-footer py-1 bg-warning bg-opacity-25 border-warning'>
        {% if table.url %}
            <a target='_blank' class='btn btn-primary btn-sm my-1' href='{{ table.url }}'>{{ name }}</a>
        {% else %}
            <span class='fw-bold'>{{ name }}</span>
        {% endif %}
        <small class='text-muted ms-2' title='{{ table.notes|join("\n") }}'>
            Advies over kiembaandiagnostiek. Geldt alleen voor (waarschijnlijk) pathogene varianten,
            bij TMB &lt; 20 mut/Mb en als de variant niet evident subklonaal is.
            {% if gene.changed %}Tekst gewijzigd ten opzichte van de vorige versie.{% endif %}
        </small>
    </div>
</div>
"""


class Secrets(BaseSettings):
    table3_database: str = "databases/table3.yml"


secrets = Secrets()

# (mtime, table), so the file is only read again when it changes
_table: tuple[float, dict] = (0, {})


def get_table() -> dict:
    """
    Returns 'Tabel 3' of the NVVP, VKGL and VKGN: for which genes a (likely) pathogenic variant
    found in a tumor is a reason to advise germline diagnostics. See the README for the format of the file.
    """
    global _table
    mtime = os.path.getmtime(secrets.table3_database)
    if _table[0] != mtime:
        with open(secrets.table3_database, encoding="utf-8") as f:
            table = yaml.safe_load(f)
        table["genes"] = {str(gene).upper(): advice or {} for gene, advice in (table.get("genes") or {}).items()}
        _table = (mtime, table)
    return _table[1]


def has_advice(gene: dict) -> bool:
    """A gene can be in the table with 'Nee' and 'geen': a variant in it is never a reason for germline diagnostics"""
    report = str(gene.get("report") or "").strip().lower()
    mtb = str(gene.get("mtb") or "").strip().lower()
    return report not in ("", "-", "nee") or mtb not in ("", "-", "geen", "nee")


class Table3(Source):
    def set_entries(self):
        self.entries = {
            ("transcript",): self.transcript,
            ("gene",): self.gene,
        }

    def is_banner(self) -> bool:
        return True

    def is_complete(self) -> bool:
        if not os.path.exists(secrets.table3_database):
            print("Could not find Tabel 3:", secrets.table3_database)
            return False
        try:
            get_table()
        except (yaml.YAMLError, AttributeError, TypeError) as e:
            print("Tabel 3 is not in the expected format:", e)
            return False
        return True

    async def transcript(self):
        """
        Looks up the gene of the transcript, so the advice is shown without waiting for another source to supply the gene
        """
        gene = await self.resolve_gene()
        if gene:
            self.report(gene)
        else:
            # this is not complete, so gene() is tried when the meta data has a gene
            self.hidden = True

    async def gene(self):
        self.report(self.variant["gene"])

    def report(self, symbol):
        """
        Shows the advice of the table for the gene, the text is shown as it is in the table (in Dutch)
        """
        table = get_table()
        gene = table["genes"].get(str(symbol).upper())
        self.complete = True

        if gene is None or not has_advice(gene):
            # most genes are not in the table, don't use space on the page to say so.
            # The same for a gene that is in the table to say that there is no advice (EGFR)
            self.found = False
            self.hidden = True
            return

        name = f"Tabel 3 ({table['version']})" if table.get("version") else "Tabel 3"
        template = Environment(loader=BaseLoader(), autoescape=True).from_string(TEMPLATE)
        self.html_text = template.render(table=table, gene=gene, name=name, highlight=HIGHLIGHT)

    def get_html(self):
        """The banner instead of the card of the other sources"""
        return self.html_text

    def get_name(self):
        return "Tabel 3"

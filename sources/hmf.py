import os

from markupsafe import escape
from pydantic_settings import BaseSettings
from util import reverse_complement

from .source_result import Source, SourceURL

# the sources of the HMF database, with the name to show for them
SOURCE_NAMES = {
    "docm": "DoCM",
    "vicc_civic": "CIViC",
    "vicc_cgi": "CGI",
    "hartwig_cohort": "HMF WGS cohort",
    "hartwig_curated": "HMF curated",
}

class Secrets(BaseSettings):
    hmf_database: str = "databases/hmf_hotspots.tsv"

secrets = Secrets()

# (mtime, {(chr, pos, ref, alt): (gene, ensembl, pdot, sources)}), so the database is only read again when it changes
_hotspots: tuple[float, dict] = (0, {})


def get_hotspots() -> dict:
    """
    Returns the HMF database as {(chr, pos, ref, alt): (gene, ensembl, pdot, sources)}
    """
    global _hotspots
    mtime = os.path.getmtime(secrets.hmf_database)
    if _hotspots[0] != mtime:
        hotspots = {}
        with open(secrets.hmf_database) as f:
            for line in f:
                columns = line.rstrip("\n").split("\t")
                if len(columns) < 8:
                    continue
                chrom, pos, ref, alt, gene, ensembl, pdot, sources = columns[:8]
                hotspots[(chrom, pos, ref, alt)] = (gene, ensembl, pdot, sources.strip())
        _hotspots = (mtime, hotspots)
    return _hotspots[1]


class HMF(Source):
    def set_entries(self):
        self.entries = {
            ("transcript", "cdot"): self.transcript_cdot,
            ("chr", "pos", "ref", "alt"): self.chr_pos_ref_alt,
        }

    def is_optional(self) -> bool:
        return True

    def is_complete(self) -> bool:
        if not os.path.exists(secrets.hmf_database):
            print("Could not find HMF hotspot database:", secrets.hmf_database)
            return False
        return True

    async def transcript_cdot(self):
        """
        The HMF database is on the forward strand of hg19, so use the genomic coordinates of the transcript:cdot
        """
        resolved = await self.resolve_coordinates()
        if resolved is None:
            self.hidden = True
            return  # chr_pos_ref_alt can still be tried when another source has the position

        self.report(self.lookup_variant(resolved.chr, resolved.pos, resolved.ref, resolved.alt))
        self.complete = True

    async def chr_pos_ref_alt(self):
        """
        For searches by position, and when the transcript:cdot could not be mapped.
        In the last case ref/alt are the bases of the cdot, so the reverse complement is tried too.
        """
        chrom = self.variant["chr"]
        pos = self.variant["pos"]
        ref = self.variant["ref"]
        alt = self.variant["alt"]

        info = self.lookup_variant(chrom, pos, ref, alt)
        if not info and ref and alt:
            info = self.lookup_variant(chrom, pos, reverse_complement(ref), reverse_complement(alt))
        self.report(info)

    def report(self, info):
        """
        Adds the meta data of the hotspot and shows which sources of the HMF database have it.
        The sources that don't have it are not listed, the card is as small as possible
        """
        if not info:
            # most variants are not a hotspot, don't use space on the page for a table of 'No'
            self.found = False
            self.hidden = True
            return

        gene, ensembl, pdot, sources = info
        sources = set(sources.split(","))

        if gene != "null":
            self.new_variant_data["gene"] = gene
        if ensembl != "null":
            self.new_variant_data["ensembl_transcript"] = ensembl
        if pdot not in ("null", "-"):
            self.new_variant_data["pdot"] = pdot

        # the sources in the order of SOURCE_NAMES, followed by sources that are new in the database
        names = [name for source, name in SOURCE_NAMES.items() if source in sources]
        names += sorted(escape(source) for source in sources - set(SOURCE_NAMES) if source)
        badges = " ".join(f"<span class='badge text-bg-success fw-normal'>{name}</span>" for name in names)
        self.html_text = f"<span class='small'>Hotspot according to</span> {badges}"

        # the name is at the bottom of the card, like the links of the other sources. There is nothing to link to
        self.html_title = ""
        label = f"<span class='btn btn-sm my-1 px-0 border-0 disabled text-muted text-start opacity-100'>{self.get_name()}</span>"
        self.html_links["main"] = SourceURL("", "", override=label)

    def lookup_variant(self, chrom, pos, ref, alt):
        """
        Searches the HMF database for the variant, returns (gene, ensembl, pdot, sources) or None
        """
        chrom = str(chrom)
        if chrom.lower().startswith("chr"):
            chrom = chrom[3:]
        return get_hotspots().get((chrom, str(pos), ref, alt))

    def get_name(self):
        return "HMF Hotspots Database"

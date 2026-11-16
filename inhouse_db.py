"""
Queries the in-house classification database, a single sqlite file holding
the variants that have been classified by the different centers (EMC, LUMC, ...)

The database has three tables:
    metadata (key, value), with the date the database was made as 'built'
    centers (name, source_file, variants)
    classifications (center, gene, chr, pos, ref, alt, classification), indexed on (chr, pos)

Variants are stored by hg19 genomic position, in the notation of normalize_alleles(),
because not every center reports a transcript, and the ones that do don't always use the same one.
"""
import re
import sqlite3
from pathlib import Path

ALLELE_RE = re.compile("^[ACGT]*$")


def normalize_chr(chrom) -> str:
    return re.sub("^chr", "", str(chrom).strip(), flags=re.IGNORECASE).upper()


def normalize_alleles(pos, ref, alt) -> tuple[int, str, str] | None:
    """
    Brings a variant to one notation so the exports of different centers can be compared:
    - an empty allele ('.' or '-') becomes ''
    - bases shared by ref and alt are removed (GC>AC becomes G>A)
    - deletions are (first deleted base, deleted bases, '')
    - insertions are (base they are inserted after, '', inserted bases)
    Returns None if this is not a variant made of A, C, G and T
    """
    ref = "" if ref is None else str(ref).strip().upper()
    alt = "" if alt is None else str(alt).strip().upper()
    ref = "" if ref in (".", "-") else ref
    alt = "" if alt in (".", "-") else alt
    if ref == alt or not ALLELE_RE.match(ref) or not ALLELE_RE.match(alt):
        return None
    try:
        pos = int(pos)
    except (TypeError, ValueError):
        return None

    trimmed = False
    while ref and alt and ref[-1] == alt[-1]:
        ref, alt, trimmed = ref[:-1], alt[:-1], True
    while ref and alt and ref[0] == alt[0]:
        ref, alt, pos, trimmed = ref[1:], alt[1:], pos + 1, True
    if not ref and trimmed:
        pos -= 1  # pos is now the first base after the insertion, we want the one before it
    return pos, ref, alt


def connect(database: str) -> sqlite3.Connection:
    """Opens the database read only"""
    return sqlite3.connect(f"{Path(database).resolve().as_uri()}?mode=ro", uri=True)


def lookup(database: str, chrom, pos_from: int, pos_to: int) -> tuple[list[str], list[tuple], str | None]:
    """
    Returns the centers in the database, every (center, pos, ref, alt, classification)
    on the chromosome between pos_from and pos_to, and the date the database was made
    """
    conn = connect(database)
    try:
        centers = [name for (name,) in conn.execute("SELECT name FROM centers ORDER BY name")]
        rows = conn.execute(
            "SELECT center, pos, ref, alt, classification FROM classifications WHERE chr = ? AND pos BETWEEN ? AND ?",
            (normalize_chr(chrom), pos_from, pos_to),
        ).fetchall()
        try:
            built = conn.execute("SELECT value FROM metadata WHERE key = 'built'").fetchone()
        except sqlite3.OperationalError:  # a database from before the date was stored
            built = None
        return centers, rows, built[0] if built else None
    finally:
        conn.close()


def left_align(pos: int, ref: str, alt: str, sequence: str, sequence_start: int) -> tuple[int, str, str]:
    """
    Moves a deletion or insertion (as returned by normalize_alleles) as far upstream as the reference allows.
    In a repeat the same variant can be written at several positions, after this they are all written the same.
    sequence is the forward strand of the reference, its first base is position sequence_start
    """
    def base(position):
        index = position - sequence_start
        return sequence[index] if 0 <= index < len(sequence) else None

    if ref and not alt:
        while base(pos - 1) == ref[-1]:
            ref = base(pos - 1) + ref[:-1]
            pos -= 1
    elif alt and not ref:
        while base(pos) == alt[-1]:
            alt = base(pos) + alt[:-1]
            pos -= 1
    return pos, ref, alt


def match(row: tuple[int, str, str], query: tuple[int, str, str], sequence: str | None = None, sequence_start: int = 0) -> str | None:
    """
    Compares a database row to the searched variant, both (pos, ref, alt) from normalize_alleles
    Returns 'exact', 'possible' or None

    Substitutions and delins have to be identical.
    Deletions and insertions are compared after left aligning both on the reference sequence.
    'possible' is for matches that rely on an assumption, the user should check those:
    - a row that looks like a deletion, but whose bases are not the reference at that position.
      Some exports write insertions that way, so it is compared as an insertion in front of pos.
    - without reference sequence: an indel of the same size next to the searched one, with the same bases rotated
    """
    if row == query:
        return "exact"

    pos, ref, alt = query
    row_pos, row_ref, row_alt = row
    if (ref and alt) or (row_ref and row_alt):
        return None

    if sequence:
        aligned_query = left_align(pos, ref, alt, sequence, sequence_start)
        if left_align(row_pos, row_ref, row_alt, sequence, sequence_start) == aligned_query:
            return "exact"
        index = row_pos - sequence_start
        if alt and row_ref and index >= 0 and sequence[index:index + len(row_ref)] != row_ref:
            if left_align(row_pos - 1, "", row_ref, sequence, sequence_start) == aligned_query:
                return "possible"
        return None

    same_kind = bool(ref) == bool(row_ref)
    bases, row_bases = ref or alt, row_ref or row_alt
    if same_kind and len(bases) == len(row_bases) and row_bases in bases + bases and abs(row_pos - pos) <= len(bases):
        return "possible"
    return None

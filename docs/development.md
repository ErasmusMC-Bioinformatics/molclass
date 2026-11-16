# Development

## Running Molclass from the source

```bash
pip install -r requirements/requirements.txt
uvicorn main:app --reload --port 8585 --host 0.0.0.0
```

The page script is written in TypeScript, `static/molclass.ts`, and compiled to `static/molclass.js`:

```bash
tsc static/molclass.ts --outfile static/molclass.js --watch --lib 'es2020,dom'
```

## How a search works

Molclass is a [FastAPI](https://fastapi.tiangolo.com/) application. After the page is loaded, it opens a websocket to the server ([`router.py`](../router.py)), and the server asks the sources about the variant and sends every card as soon as its source has answered.

Each source says which information it needs, for example a transcript and a coding change, or a dbSNP identifier. The server calls the sources in rounds: in every round, each source whose information is known runs, and adds what it found (the gene, the protein change, …) to what is known about the variant. The next round can then run the sources that needed that. When no source can run anymore, the search is done.

For example, a search for `rs1057519915` with only dbSNP and Clingen switched on:

1. Only dbSNP can run, because only the `rs` number is known. It adds the transcript (`NM_004958.4`) and the coding change (`c.7500T>G`).
2. Clingen can now run, with the transcript and coding change.
3. No source is left, so the search ends.

Sources can disagree, for example on the transcript. What was searched always wins; otherwise Molclass takes what most sources say, and marks a card that disagrees with a warning sign.

## Genomic coordinates

Sources that need the genomic position of a `transcript:cdot` should not look it up themselves, but use the methods of `Source` ([`sources/source_result.py`](../sources/source_result.py)), which use [`coordinates.py`](../coordinates.py):

| Method | Returns |
|---|---|
| `await self.resolve_coordinates(build="GRCh37")` | Chromosome, position, ref and alt as in a VCF, on the forward strand, and the hgvs genomic notation |
| `await self.resolve_gdot(build="GRCh37")` | Only the hgvs genomic notation, which is faster for deletions and insertions |
| `await self.resolve_gene()` | The gene of the searched transcript |

A variant is looked up only once, also when several sources ask for it at the same time, and the result is kept for the next search. The position comes from Mutalyzer, or from Ensembl VEP for what Mutalyzer can't map; the reference genome from Ensembl or UCSC. A request that fails is tried again (`RETRY_WAITS` in `coordinates.py`).

The result is also added to what is known about the variant, as `gdot`, `g_chr`, `g_pos`, `g_ref` and `g_alt` (`gdot38`, `g38_chr`, … for GRCh38). `gdot` and `gdot38` are shown at the top of the page. The older `ref` and `alt` are the bases of the coding change, so for a gene on the reverse strand they are not the genomic bases.

If none of the sources found the gene, protein change or genomic positions, Molclass looks them up itself at the end of the search (`complete_variant` in `router.py`), so the boxes at the top of the page are always filled for a `transcript:cdot`.

## Adding a source

1. Add a class in [`sources/`](../sources/) that inherits from `Source`, and list it in `sources/__init__.py`.
2. In `set_entries()`, say which information it needs and which method to call with it:
   ```python
   def set_entries(self):
       self.entries = {
           ("transcript", "cdot"): self.transcript_cdot,
           ("gene",): self.gene,
       }
   ```
3. In that method, fill the card: `self.html_text`, the buttons in `self.html_links`, and `self.found = False` when the source doesn't have the variant. Information for other sources goes into `self.new_variant_data`. Set `self.complete = True` when the source is done; otherwise it is called again in the next round, with the next entry it can use.
4. Add the class to `sources` in [`config.py`](../config.py); the order of that list is the order of the cards on the page. `source_widths` and `stacked_sources` set how wide a card is and which cards share a column.

A few methods of `Source` change how the card is shown:

| Method | Effect |
|---|---|
| `is_complete()` | Return `False` to leave the source out, for example when its API key is not set |
| `is_link()` | The source is only a link: it is a button on the Extra links card instead of a card of its own |
| `is_optional()` | The card is only shown when the source has something for the variant |
| `is_banner()` | The card is shown across the full width, above the others |

Use `self.async_get_json()` and the other request methods of `Source`, so the requests share one session and a timeout is shown on the card. A source that queries an external service should identify itself and not repeat requests the service refused; see [`sources/lovd.py`](../sources/lovd.py).

## Building a Windows executable

```powershell
env/Scripts/Activate.ps1
pyinstaller --clean molclass.spec
```

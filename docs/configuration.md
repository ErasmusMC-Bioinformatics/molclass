# Configuration

Molclass works without any configuration, with the public sources. This page describes how to switch on the cards that need a data file, a licence or an API key, in the order in which the cards appear on the page.

## How settings are passed

Every setting is an environment variable. The easiest way is to put them in a file, here `molclass.env`, and the data files in a folder, here `databases/`, and to pass both to the container:

```bash
docker run -d --name molclass -p 8080:8080 \
    --env-file molclass.env \
    -v "$(pwd)/databases:/app/databases:ro" \
    molclass
```

```ini
# molclass.env
TABLE3_DATABASE=databases/table3.yml
INHOUSE_DATABASE=databases/inhouse.db
ALPHAGENOME_API_KEY=...
DISABLED_SOURCES=Varsome,Mastermind
```

The data files are read from `databases/` by default, so with the folder mounted as above the `..._DATABASE` settings are only needed for other file names. A data file can be replaced while Molclass is running: it is read again on the next search.

> [!WARNING]
> `molclass.env` holds your API keys and `databases/` your classifications. Keep both out of git; they are already in `.gitignore` and `.dockerignore`.

## Tabel 3

Shows the advice of "Tabel 3" of the NVVP, VKGL and VKGN for the gene: when a (likely) pathogenic variant found in a tumour is a reason to advise germline testing, in the pathology report and in the MTB.

The table is published as a PDF, so it has to be typed over into YAML:

```yml
version: maart 2026
url: "https://artsengenetica.nl/sites/default/files/Versie%20tabel%203%20maart%202026.pdf"
columns:
  report: Attenderen op mogelijke kiembaanvariant in PA-verslag indien sprake is van onderstaande tumor/beeld
  mtb: Aanvullende redenen om te overwegen te verwijzen voor klinische genetische counseling
notes:
  - Alleen indien TMB < 20 mut/Mb.
genes:
  ATM:
    report: Pancreas- of mammacarcinoom
    mtb: Bij pancreas- of mammacarcinoom bij patiënt of bij 1e gr verwant
  BRCA1:
    report: Altijd
  RET:
    changed: true
    remark: N.B. RET fusies zijn geen reden voor kiembaanonderzoek
    report: |-
      Codon 918 nooit
      Codon 634 en 833 bij elk tumortype
```

- `version` and `url` are shown on the button of the card, which opens the PDF.
- `report` and `mtb` are the two columns of the table; `columns` and `notes` are shown when hovering over the card.
- `changed` marks a text that changed since the previous version, `remark` is shown above the advice.

| Setting | Default |
|---|---|
| `TABLE3_DATABASE` | `databases/table3.yml` |

## Previously classified

Shows whether one of the participating centres has classified the variant before, and how. The classifications are read from a SQLite database; the card shows the date the database was made.

Variants are stored by their hg19 position (chromosome, position, ref, alt), because not every centre reports a transcript, or the same one. A searched `transcript:cdot` is converted to hg19 by Molclass, and deletions and insertions are left aligned before they are compared, so it doesn't matter where in a repeat a centre reported them.

The database has three tables:

| Table | Columns |
|---|---|
| `metadata` | `key`, `value`; the date the database was made, as `2026-10-10`, under the key `built` |
| `centers` | `name`, `source_file`, `variants` |
| `classifications` | `center`, `gene`, `chr`, `pos`, `ref`, `alt`, `classification`, with an index on (`chr`, `pos`) |

`chr` is written without `chr` (`7`, `X`); `pos`, `ref` and `alt` as described in `normalize_alleles()` in [`inhouse_db.py`](../inhouse_db.py): bases that ref and alt share are removed, so a deletion is (first deleted base, deleted bases, empty) and an insertion is (base before it, empty, inserted bases). The classifications are shown as they are written, in the colours of benign, VUS and pathogenic.

| Setting | Default |
|---|---|
| `INHOUSE_DATABASE` | `databases/inhouse.db` |

## AlphaGenome

Shows the AlphaGenome Variant Impact score from the [AlphaGenome Atlas](https://deepmind.google.com/science/alphagenome/atlas): where the variant is in the distribution of all variants, and the features the score is based on. The Atlas only has scores for substitutions of a single base, on GRCh38; Molclass looks up the hg38 position itself.

> [!IMPORTANT]
> The terms of the AlphaGenome API allow research use only. Check them before you switch the card on in a diagnostic setting.

| Setting | |
|---|---|
| `ALPHAGENOME_API_KEY` | Your AlphaGenome API key |

## Gene lists

Shows whether the gene of the variant is on one of your own lists, with a message and a link:

```yml
- name: Sonic
  message: This gene is named after a videogame character.
  url: https://en.wikipedia.org/wiki/Sonic_the_Hedgehog
  genes:
    - SHH
```

| Setting | Default |
|---|---|
| `GENE_LISTS` | `databases/gene_lists.yml` |

## Alamut

The buttons of the card open the variant in Alamut Visual Plus on the user's own computer. Molclass can also ask the Alamut API for information about the variant; that needs a computer running Alamut that the Molclass server can reach.

| Setting | |
|---|---|
| `ALAMUT_IP` | The IP address of the computer running Alamut |
| `ALAMUT_INSTITUTION` | Your institution ID |
| `ALAMUT_API_KEY` | Your Alamut API key |

All three are needed for the card to be shown.

## COSMIC

Shows the entries of the variant in the COSMIC Cancer Mutation Census. Download the file `Cosmic_MutantCensus_*_GRCh37.tsv.gz` from the "Census Genes Mutations" section of the [COSMIC downloads](https://cancer.sanger.ac.uk/cosmic/download) (an account is needed) and put it in `databases/`.

| Setting | Default |
|---|---|
| `COSMIC_DATABASE` | `databases/Cosmic_MutantCensus_v98_GRCh37.tsv.gz` |

## OncoKB

The OncoKB interpretation of the variant is always shown on the Genome Nexus card. The full OncoKB card, with the treatments, needs an API key, which you find under your [OncoKB account settings](https://www.oncokb.org/account/settings).

| Setting | |
|---|---|
| `ONCOKB_API_KEY` | Your OncoKB API key |

## HMF hotspots

Shows whether the [Hartwig Medical Foundation](https://www.hartwigmedicalfoundation.nl/en/) lists the variant as a known hotspot, and according to which sources. The card is only shown for variants that are on the list.

The file is a TSV without a header, one variant per line, on hg19:

```
1	11169360	TC	AG	MTOR	ENST00000361445	p.R2505P	docm,vicc_cgi
```

The columns are chromosome, position, ref, alt, gene, Ensembl transcript, protein change, and the sources, separated by commas (`docm`, `vicc_civic`, `vicc_cgi`, `hartwig_cohort`, `hartwig_curated`). They come from the `KnownHotspots.somatic.37.vcf.gz` of the Hartwig resources.

| Setting | Default |
|---|---|
| `HMF_DATABASE` | `databases/hmf_hotspots.tsv` |

## Switching cards off

`DISABLED_SOURCES` takes a comma-separated list of the class names of the sources, as listed in [`config.py`](../config.py):

```ini
DISABLED_SOURCES=Varsome,Mastermind,dbSNP
```

import os
import csv

from pydantic import BaseSettings, Field

from gzip import open as gzip_open

from .source_result import Source, SourceURL

class Secrets(BaseSettings):
    cosmic_database: str = Field(default="databases/Cosmic_MutantCensus_v98_GRCh37.tsv.gz", env="COSMIC_DATABASE")

secrets = Secrets()

class COSMIC(Source):
    def set_entries(self):
        self.entries = {
            ("gene", "cdot"): self.gene_cdot,
            ("gene", ): self.gene,
        }

    def is_complete(self) -> bool:
        if not os.path.exists(secrets.cosmic_database):
            print(f"Did not find cosmic DB {secrets.cosmic_database}")
            return False
        return True

    async def gene(self):
        gene = self.variant["gene"]
        
        url = f"https://cancer.sanger.ac.uk/cosmic/gene/analysis?ln={gene}"

        self.html_links["main"] = SourceURL("Go", url)

    async def gene_cdot(self):
        """
        Cosmic reads through the database file until it finds the gene/cdot
        """
        gene = self.variant["gene"] 
        cdot = self.variant["cdot"]

        url = f"https://cancer.sanger.ac.uk/cosmic/gene/analysis?ln={gene}"

        self.html_links["main"] = SourceURL("Go", url)

        cosmic_db_dirname = os.path.dirname(secrets.cosmic_database)

        # create an 'optimized' database, just removing columns so it's faster to parse/iterate
        optim_db_path = os.path.join(cosmic_db_dirname, "cosmic_database.tsv.gz")
        if not os.path.exists(optim_db_path):
            self.log_info("Creating optimized database")
            with gzip_open(secrets.cosmic_database, 'rt') as full_handle, gzip_open(optim_db_path, 'wt') as optim_handle:
                reader = csv.DictReader(full_handle, delimiter="\t")
                writer = csv.DictWriter(optim_handle, delimiter="\t", fieldnames=["gene", "cosmic_id", "cdot", "pdot"])
                for row in reader:
                    writer.writerow({
                        "gene": row["GENE_SYMBOL"],
                        "cosmic_id": row["LEGACY_MUTATION_ID"],
                        "cdot": row["MUTATION_CDS"],
                        "pdot": row["MUTATION_AA"],
                    })

        cosmic_count = 0
        cosmic_id = ""
        # meh, should use aiofiles for async, but that is SLOOOW (minutes...)
        with gzip_open(optim_db_path, 'rt') as db_handle:
            reader = csv.DictReader(db_handle, delimiter="\t", fieldnames=["gene", "cosmic_id", "cdot", "pdot"])
            for row in reader:
                row_gene = row["gene"]
                if row_gene != gene:
                    continue
                row_cdot = row["cdot"]
                if row_cdot != cdot:
                    continue
            
                cosmic_count += 1
                cosmic_id = row["cosmic_id"]

        if cosmic_count and cosmic_id:
            self.html_subtitle = cosmic_id
            cosmic_variant_url = f"https://cancer.sanger.ac.uk/cosmic/search?genome=37&q={cosmic_id}"
            self.html_links["main"] = SourceURL("Go", cosmic_variant_url)

            self.html_text = f"<p class='h6'>Count: {cosmic_count}</p>"

        self.complete = True


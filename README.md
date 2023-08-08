# Molclass

Moleculair classification tool, enter your search query, and results from multiple sources (dbSNP, Franklin, Clinvar, etc) will be aggregated

Molclass is available as a Docker container:  
`docker run -p 8080:8080 ghcr.io/erasmusmc-bioinformatics/molclass:latest`  

And connect to Molclass on [http://127.0.0.1:8080](http://127.0.0.1:8080).

## HMF

The [Hartwig Medical Foundation](https://www.hartwigmedicalfoundation.nl/en/) has a curated list of variants that can be used as a source, to enable it set the path to the database file with the `HMF_DATABASE` environment variable, for example with Docker:  
```
docker run \
    -p 8080:8080 \
    -v /host/path/to/hmf_hotspots.tsv:/databases/hmf_hotspots.tsv \
    -e HMF_DATABASE=/databases/hmf_hotspots.tsv \
    ghcr.io/erasmusmc-bioinformatics/molclass:latest
```

## OncoKB

[OncoKB](https://www.oncokb.org) can be used as a source if you have an API key, it can be found under your [account settings](https://www.oncokb.org/account/settings).  
The OncoKB API key can be added through the `ONCOKB_API_KEY` environment variable, for example with Docker:  
```
docker run \
    -p 8080:8080 \
    -e ONCOKB_API_KEY=<api-key> \
    ghcr.io/erasmusmc-bioinformatics/molclass:latest
```
## Alamut

Molclass can also connect to the Alamut API, this requires a computer running the Alamut client that Molclass can query.  
For Molclass to connect to this Alamut client, 3 environment variable need to be set:  
- `ALAMUT_IP`: the IP address of the machine running the Alamut client
- `ALAMUT_INSTITUTION`: Your institution ID
- `ALAMUT_API_KEY`: Your API key

For example with Docker:  
```
docker run \
    -p 8080:8080 \
    -e ALAMUT_IP=127.0.0.1 \
    -e ALAMUT_INSTITUTION=<institution-id> \
    -e ALAMUT_API_KEY=<api-key> \
    ghcr.io/erasmusmc-bioinformatics/molclass:latest
```

## Cosmic

To use Cosmic, the Mutant Census database must be downloaded and configured.
The database can be downloaded [https://cancer.sanger.ac.uk/cosmic/download] if you have an account, from the "Census Genes Mutations" section, then set the `COSMIC_DATABASE` environment variable to the path of the downloaded file, for example with Docker: 
```
docker run \
    -p 8080:8080 \
    -v /host/path/to/Cosmic_MutantCensus_v98_GRCh37.tsv.gz:/databases/Cosmic_MutantCensus_v98_GRCh37.tsv.gz \
    -e COSMIC_DATABASE=/databases/Cosmic_MutantCensus_v98_GRCh37.tsv.gz \
    ghcr.io/erasmusmc-bioinformatics/molclass:latest
```

## Uvicorn start

`uvicorn main:app --reload --port 8585 --host 0.0.0.0`

## Typescript compile

`tsc static/molclass.ts --outfile static/molclass.js --watch --lib 'es2020,dom'`
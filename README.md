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

# Production

On every new release a Github action will trigger a new Docker build for `ghcr.io/erasmusmc-bioinformatics/molclass`.  
The production environment uses this image in `docker-compose.yml` to run the Molclass production server.  
The production Molclass server is running at CIT, first ssh to the jumpoff server, `creig.erasmusmc.nl`, then ssh to `p-molclass01`.
Execute a `docker-compose pull` to pull the newly released image and then `docker-compose up -d --build` to restart the service with the updated release image.

## SSL certificate update

Make a copy of the old cert/key:  
```bash
cp /etc/nginx/certs/bifrost.erasmusmc.nl.crt /etc/nginx/certs/bifrost.erasmusmc.nl.crt.2023.old
cp /etc/nginx/certs/bifrost.erasmusmc.nl.key /etc/nginx/certs/bifrost.erasmusmc.nl.key.2023.old
```

Overwrite with the new cert/key:  
```bash
mv bifrost.erasmusmc.nl.crt /etc/nginx/certs/bifrost.erasmusmc.nl.crt
mv bifrost.erasmusmc.nl.key /etc/nginx/certs/bifrost.erasmusmc.nl.key
```

Restart the httpproxy docker:  
```bash
docker restart httpproxy
```

# Dev

## Structure

Molclass is a FastAPI webserver where, after an [initial page load](https://github.com/ErasmusMC-Bioinformatics/molclass/blob/a720b52c56ea0ac707ac9e3ea0eda34134e5f6dd/router.py#L33), the client [connects back](https://github.com/ErasmusMC-Bioinformatics/molclass/blob/a720b52c56ea0ac707ac9e3ea0eda34134e5f6dd/static/molclass.ts#L6) to the webserver to a [websocket](https://github.com/ErasmusMC-Bioinformatics/molclass/blob/a720b52c56ea0ac707ac9e3ea0eda34134e5f6dd/router.py#L129) to allow for asynchronous querying/updating of sources.  

[Sources define](https://github.com/ErasmusMC-Bioinformatics/molclass/blob/a720b52c56ea0ac707ac9e3ea0eda34134e5f6dd/sources/source_result.py#L64) what meta data they need to be able to complete a request and Molclass will iteratively call sources as more meta data becomes available.  

Each source adds the meta data it gets to the pool of available meta data.  
It is possible that sources return different meta data.
For example, searching [NM_000267.3:c.5286T>A](http://molclass.erasmusmc.nl/search?search=NM_000267.3%3Ac.5286T%3EA) where Clingen and Franklin both prefer `NM_001042492.3:c.5349T>A`.  
The meta data in the search always has precedence over the sources, but in other cases Molclass counts how many sources agree and picks the majority.
### Simple search example
If only the [dbSNP](https://github.com/ErasmusMC-Bioinformatics/molclass/blob/a720b52c56ea0ac707ac9e3ea0eda34134e5f6dd/sources/dbsnp.py#L45) and [Clingen](https://github.com/ErasmusMC-Bioinformatics/molclass/blob/a720b52c56ea0ac707ac9e3ea0eda34134e5f6dd/sources/clingen.py#L13C10-L13C10) sources were active and the user searched for `rs1057519915`, Molclass would:  

In the first iteration only query dbSNP because Molclass only has an `rs#`.  
It adds the `transcript` (`NM_004958.4`) and `cdot` (`c.7500T>G`) to the meta data pool (+other meta data)

In the second iteration Molclass can now call `Clingen` with the `transcript`/`cdot` values it got from the first iteration.

The third iteration Molclass will see that there are no more sources left, and end the iteration.

## Uvicorn start

`uvicorn main:app --reload --port 8585 --host 0.0.0.0`

## Typescript compile

`tsc static/molclass.ts --outfile static/molclass.js --watch --lib 'es2020,dom'`

## Build PyInstaller

Activate the venv:  
`env/Scripts/Activate.ps1`

And run: 
`pyinstaller --clean --name molclass --onefile main.py`
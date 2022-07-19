# Molclass

Moleculair classification tool, enter your search query, and results from multiple sources (dbSNP, Franklin, Clinvar, etc) will be aggregated

## Uvicorn start

`uvicorn main:app --reload --port 8585 --host 0.0.0.0`

## Typescript compile

`tsc static/molclass.ts --outfile static/molclass.js --watch --lib 'es2020,dom'`
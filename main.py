import copy

from types import MappingProxyType

import aiohttp
import asyncio

from typing import List
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

from fastapi.templating import Jinja2Templates

from config import settings
from sources.source_result import Source
from search import parse_search, parse_transcript

import yaml


import logging
import os

with open('compose/molclass/logging.yaml') as f:
    config = yaml.load(f, Loader=yaml.FullLoader)
    logging.config.dictConfig(config)





app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(
        "index.html.jinja2", 
        {
            "request": request,
        }
    )

@app.get("/search", response_class=HTMLResponse)
def search(request: Request, search: str):
    websocket_url = f"{request.base_url}ws/{search}"
    websocket_url = websocket_url.replace("https:", "ws:").replace("http:", "ws:")
    return templates.TemplateResponse(
        "index.html.jinja2", 
        {
            "request": request,
            "search": search,
            "sources": [source({}, {}) for source in settings.sources],
            "websocket_url": websocket_url,
        }
    )

@app.get("/info")
def info():
    return settings.dict()

def merge_variant_data(source: Source, consensus: dict):
    for key, value in source.new_variant_data.items():
        if key in consensus:
            if value in consensus[key]:
                consensus[key][value] = list(set(consensus[key][value] + [source.name]))  # list(set()) for lazy unique
            else:
                consensus[key][value] = [source.name]
        else:
            consensus[key] = {value: [source.name]}
    source.new_variant_data.clear()

async def new_variant_from_consensus(consensus: dict, variant: dict, search: dict, websocket: WebSocket):
    variant.clear()
    for key, values in consensus.items():
        value = max(values, key=lambda k: len(set(values[k])))  # what value has the most source 'votes', set() to remove duplicates
        variant[key] = value
    
    for key, value in search.items():
        if key in variant:
            if variant[key] != value:
                await send_log(f"{key} has different value then search ({value}): {consensus[key]}", websocket)
        variant[key] = value

def check_source_consensus(consensus: dict, variant: dict, sources: list[Source]):
    sources = {source.name: source for source in sources}
    for key, values in consensus.items():
        if key not in ["transcript", "cdot", "gene", "pdot", "ref", "alt"]:
            continue
        for value, srcs in values.items():
            if key == "transcript":  # only compare transcript without version
                nm1 = parse_transcript(str(variant[key]))["transcript_number"]
                nm2 = parse_transcript(str(value))["transcript_number"]
                if nm1 == nm2:
                    continue
            elif str(variant[key]) == str(value):
                continue
            
            for source in srcs:
                if source in sources:  # consensus also contains sources from previous iterations, sources doesn't
                    sources[source].matches_consensus = False
                    sources[source].matches_consensus_tooltip.append(f"{key}={value}<>{variant[key]}")

async def send_log(message, websocket: WebSocket, level="info", source="System"):
    if type(message) == str:
        message = [{
            "level": level,
            "source": source,
            "message": message,
        }]
    await send_logs(message, websocket)

async def send_logs(logs, websocket: WebSocket):
    await websocket.send_json({
        "type": "log",
        "messages": logs
    })

async def send_source(data: Source, websocket: WebSocket):
    await websocket.send_json({
        "type": "update",
        "name": str(data),
        "data": data.get_html(),
        "found": data.found,
        "timeout": data.timeout,
    })

async def send_variant(variant: dict, websocket: WebSocket):
    await websocket.send_json({
        "type": "variant",
        "data": variant,
    })

async def send_consensus(consensus: dict, websocket: WebSocket):
    await websocket.send_json({
        "type": "consensus",
        "data": consensus
    })

@app.websocket("/ws/{search}")
async def websocket_endpoint(websocket: WebSocket, search: str):
    await websocket.accept()
    try:
        iteration = 0
        max_iterations = 7
        variant = parse_search(search)
        ro_variant = MappingProxyType(variant)
        previous_variant = {}
        search_variant = MappingProxyType(dict(**variant))  # these values should never change
        
        consensus_variant = {k: {v: ["search"]} for k, v in search_variant.items()}  # stores for every key/value how many sources 'agree' with the value
        sources: List[Source] = [source(ro_variant, consensus_variant) for source in settings.sources]

        await send_log(f"Starting with: {variant}", websocket)
        
        while True:
            iteration += 1
            previous_variant = copy.deepcopy(variant)
        
            timeout = aiohttp.ClientTimeout(total=10)
            user_agent_header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0"}
            async with aiohttp.ClientSession(timeout=timeout, headers=user_agent_header) as session:
                tasks = []
                for source in sources:
                    tasks.append(asyncio.ensure_future(source.execute(session)))
                
                source_results: List[Source] = await asyncio.gather(*tasks)

            source_results = [source_result for source_result in source_results if source_result]
            
            if not source_results:
                await send_log(f"No more sources to query, stopping", websocket)
                break
            else:
                await send_log(f"Iteration {iteration}, queried {', '.join(str(source) for source in source_results if source.executed)}", websocket)

            for source in source_results:
                if source.executed:
                    merge_variant_data(source, consensus_variant)
            
            await new_variant_from_consensus(consensus_variant, variant, search_variant, websocket)
            check_source_consensus(consensus_variant, variant, sources)

            for source in source_results:
                await send_logs(source.consume_logs(), websocket)
                if source.executed or source.timeout:
                    await send_source(source, websocket)
                if source.complete:
                    sources.remove(source)
            """ # probably not needed, next if is better check?
            if variant == previous_variant:
                await send_log(f"No new variant info this iteration, stopping", websocket)
                await send_consensus(consensus_variant, websocket)
                break
            """
            if not source_results:
                await send_log(f"No sources queried this iteration, stopping", websocket)
                await send_consensus(consensus_variant, websocket)
                break
            
            await send_variant(variant, websocket)

            await send_consensus(consensus_variant, websocket)

            if iteration >= max_iterations:
                await send_log(f"Reached max iterations: {iteration}/{max_iterations}, stopping", websocket)
                break
        
        if sources:
            await send_log(f"Sources not completed: {', '.join([str(source) for source in sources])}", websocket)
        else:
            await send_log(f"Used all sources.", websocket)

    except WebSocketDisconnect:
        websocket.close()
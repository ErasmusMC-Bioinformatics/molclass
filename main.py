import copy

from http.client import HTTPResponse
from typing import List
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

from fastapi.templating import Jinja2Templates

from config import settings
from util import get_variant_from_string

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
    variant = get_variant_from_string(search)
    sources = []
    for source in settings.sources:
        result = source(variant, request)
        if not result:
            continue
        sources.append(result)
    
    if "gene" in variant and variant["gene"].strip() == "TP53":
        sources.append("")

    return templates.TemplateResponse(
        "index.html.jinja2", 
        {
            "request": request,
            "search": search,
            "variant": variant,
            "sources": sources
        }
    )

@app.get("/info")
def info():
    return settings.dict()

@app.get("/new", response_class=HTMLResponse)
def new(request: Request, search: str):
    websocket_url = f"{request.base_url}ws/{search}"
    websocket_url = websocket_url.replace("https:", "ws:").replace("http:", "ws:")
    return templates.TemplateResponse(
        "new.html.jinja2", 
        {
            "request": request,
            "search": search,
            "entries": settings.entries,
            "websocket_url": websocket_url,
        }
    )















import re
RS_RE = re.compile("(?P<rs>rs[0-9]+)", re.IGNORECASE)

def parse_search(search) -> dict:
    result = {}
    if m := RS_RE.search(search):
        result.update(m.groupdict())
    
    return result


def get_sources_to_query(variant, all_sources):
    sources_to_query = []
    for source_label, entries in all_sources.items():  # for all the sources
        remove_entry = None
        for entry, entry_fun in entries.items():  # for every entry in a source - ('rs', ): <source function>
            has_all_keys = all([k in variant for k in entry])
            if has_all_keys:  # if the variant has all the information needed to query this source
                sources_to_query.append((source_label, entry_fun))
                remove_entry = entry
                break
        if remove_entry:  # remove the entry if it's been picked, to prevent it being used again
            entries.pop(remove_entry)
    return sources_to_query

import aiohttp
import asyncio

async def get_source_result(session: aiohttp.ClientSession, source):
    async with session.get(source.get) as resp:
        return await resp.text()

async def get_from_sources(sources_to_query):
    timeout = aiohttp.ClientTimeout(total=10)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        tasks = []
        for source in sources_to_query:
            url = None


@app.websocket("/ws/{search}")
async def websocket_endpoint(websocket: WebSocket, search: str):
    await websocket.accept()
    try:
        variant = parse_search(search)
        all_sources = copy.deepcopy(settings.entries)  # deepcopy so we can remove entries we already tried

        sources_to_query = get_sources_to_query(variant, all_sources)
        
        query_results = {source: source_fun(variant) for source, source_fun in sources_to_query}
        await websocket.send_json(query_results)
    except WebSocketDisconnect:
        websocket.close()


# async steps
# 1 get the sources that can be called with current variant keys: ("gene", ) if 'gene' is present
# 2 for every source, get the response html (async)
# 3 for every response html parse it (if needed) and add extra info into variant dict
# goto 1 if not all sources have be accessed or no new data added to variant dict
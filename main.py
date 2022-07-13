import copy

import aiohttp
import asyncio

from typing import List
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

from fastapi.templating import Jinja2Templates

from config import settings
from sources.source_result import Source
from search import parse_search

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
            "sources": settings.entries,
            "websocket_url": websocket_url,
        }
    )

@app.get("/info")
def info():
    return settings.dict()

def merge_variant_data(variant: dict, new_data: dict):
    # TODO better merging, with logging of conflicts
    variant.update(new_data)

async def send_log(messages, websocket: WebSocket, level="info"):
    if type(messages) == str:
        messages = [messages]
    await websocket.send_json({
        "type": "log",
        "level": level,
        "messages": messages
    })

async def send_source(data, websocket: WebSocket):
    await websocket.send_json({
        "type": "update",
        "name": str(data),
        "data": data.html,
    })

@app.websocket("/ws/{search}")
async def websocket_endpoint(websocket: WebSocket, search: str):
    await websocket.accept()
    try:
        iteration = 0
        max_iterations = 5
        variant = {}
        updated_variant = parse_search(search)
        sources: List[Source] = [source(updated_variant) for source in settings.entries]

        await send_log(f"Starting with: {updated_variant}", websocket)
        
        while variant != updated_variant and iteration <= max_iterations:
            iteration += 1
            variant = copy.deepcopy(updated_variant)
        
            timeout = aiohttp.ClientTimeout(total=10)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                tasks = []
                for source in sources:
                    tasks.append(asyncio.ensure_future(source.execute(session)))
                
                source_results: List[Source] = await asyncio.gather(*tasks)

            source_results = [source_result for source_result in source_results if source_result]
            
            await send_log(f"Iteration {iteration}, queried {', '.join(str(source) for source in source_results if source.executed)}", websocket)

            for source in source_results:
                if source.error:
                    await send_log(source.log, websocket, level="error")
                elif source.complete:
                    await send_log(f"{source} completed", websocket)
                    sources.remove(source)
                
                merge_variant_data(updated_variant, source.new_variant_data)
                await send_source(source, websocket)


    except WebSocketDisconnect:
        websocket.close()
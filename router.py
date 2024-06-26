from typing import List
from types import MappingProxyType

import aiohttp
import asyncio
import copy


from fastapi import APIRouter
from fastapi import Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

from config import settings
from sources.source_result import Source
from search import parse_search, parse_transcript

from templates import templates

router = APIRouter(
    tags=["root"],
)

@router.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(
        "index.html.jinja2", 
        {
            "request": request,
            "release_tag": settings.release_tag,
        }
    )

@router.get("/search", response_class=HTMLResponse)
def search(request: Request, search: str):
    # had some problems with getting the proper server url from the client
    # so create the url on the server and just pass it on
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

@router.get("/info")
def info():
    return settings.dict()

def merge_variant_data(source: Source, consensus: dict):
    """
    Merges the meta data from source into the consensus dict
    If consensus is:
    {
        "transcript": {
            "NM1234.1": ["dbSNP"],
            "NM1234.2": ["ClinVar"]
        },
        "gene": {
            "ABC": ["dbSNP"],
            "ABCD": ["ClinVar"]
        }
    }

    And a Clingen source with the following data as a parameter is given:
    {
        "transcript": "NM1234.1",
        "gene": "ABCD"
    }

    Then the resulting consensus dict is:  
    {
        "transcript": {
            "NM1234.1": ["dbSNP", "ClinGen"],
            "NM1234.2": ["ClinVar"]
        },
        "gene": {
            "ABC": ["dbSNP"],
            "ABCD": ["ClinGen", "ClinVar"]
        }
    }
    """
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
    """
    consensus dict will contain the consensus of 'source'
    So if source contains: 
    {
        "transcript": {
            "NM1234.1": ["dbSNP", "ClinGen"],
            "NM1234.2": ["ClinVar"]
        },
        "gene": {
            "ABC": ["dbSNP"],
            "ABCD": ["ClinGen", "ClinVar"]
        }
    }
    Then consensus will be: 
    {
        "transcript": "NM1234.1",
        "gene": "ABCD"
    }

    This example ignores the meta data in the search query, which always takes precedence
    """
    # count the number of sources for a meta data item value
    variant.clear()
    for key, values in consensus.items():
        value = max(values, key=lambda k: len(set(values[k])))  # what value has the most source 'votes', set() to remove duplicates
        variant[key] = value
    
    # check what values are different from the search query
    for key, value in search.items():
        if key in variant:
            if variant[key] != value:
                await send_log(f"{key} has different value then search ({value}): {consensus[key]}", websocket)
        variant[key] = value

def check_source_consensus(consensus: dict, variant: dict, sources: list[Source]):
    """
    Check some meta data and add warnings if there isn't a unanimous consensus for them
    """
    sources = {source.name: source for source in sources} # type: ignore
    for key, values in consensus.items():
        if key not in ["transcript", "cdot", "gene", "pdot", "ref", "alt"]:
            continue
        for value, srcs in values.items():
            # for transcripts we only want to check the main transcript, not the version, so handle that separately
            if key == "transcript":  
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
    """
    Uses the websocket to send single log with the given log level and source name
    This simply puts the log into a list and passes it on to send_logs()
    """
    if type(message) == str:
        message = [{
            "level": level,
            "source": source,
            "message": message,
        }]
    await send_logs(message, websocket)

async def send_logs(logs, websocket: WebSocket):
    """
    Use the websocket to send a list of logs to the client, adding the 'log' type attribute
    """
    await websocket.send_json({
        "type": "log",
        "messages": logs
    })

async def send_source(data: Source, websocket: WebSocket):
    """
    Send a source update to the client through the websocket
    """
    await websocket.send_json({
        "type": "update",
        "name": str(data),
        "data": data.get_html(),
        "found": data.found,
        "timeout": data.timeout,
    })

async def send_variant(variant: dict, websocket: WebSocket):
    """
    Send a variant update to the client through the websocket
    """
    await websocket.send_json({
        "type": "variant",
        "data": variant,
    })

async def send_consensus(consensus: dict, websocket: WebSocket):
    """
    Send the latest consensus to the client through the websocket
    """
    await websocket.send_json({
        "type": "consensus",
        "data": consensus
    })

@router.websocket("/ws/{search}")
async def websocket_endpoint(websocket: WebSocket, search: str):
    """
    The websocket that the client connects to, most of the server side work is handled from here
    """
    await websocket.accept()
    try:
        # it's probably impossible for molclass to get stuck querying sources for ever
        # but to be sure just cap it at something because why not
        iteration = 0
        max_iterations = 7

        variant = parse_search(search)
        ro_variant = MappingProxyType(variant)
        previous_variant = {}

        # wrap the search query meta data in a read only dict
        search_variant = MappingProxyType(dict(**variant))
        
        # holds the 'votes' for meta data values
        consensus_variant = {k: {v: ["search"]} for k, v in search_variant.items()}

        # init the active sources
        sources: List[Source] = [source(ro_variant, consensus_variant) for source in settings.sources]

        await send_log(f"Starting with: {variant}", websocket)
        
        while True:
            iteration += 1
            previous_variant = copy.deepcopy(variant)

            # set a total timout for all sources, so users don't end up waiting a long time for a slow source
            timeout = aiohttp.ClientTimeout(total=10)

            # optionally spoof our user agent to stop sources from complaining <.<
            # user_agent_header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0"}

            # the ClientSession is used by all sources for requests, allowing for async/await
            async with aiohttp.ClientSession(timeout=timeout,trust_env=True) as session: # , headers=user_agent_header
                # gather all the current sources and prepare an asyncio task list
                tasks = []
                for source in sources:
                    tasks.append(asyncio.ensure_future(source.execute(session)))
                
                # asynchronously execute all the source tasks 
                source_results: List[Source] = await asyncio.gather(*tasks)

            # if a source is missing the required meta data it returns None, filter those out here
            source_results = [source_result for source_result in source_results if source_result]
            
            # if there are no source results we're done and can stop iterating
            if not source_results:
                await send_log(f"No more sources to query, stopping", websocket)
                break
            else:
                await send_log(f"Iteration {iteration}, queried {', '.join(str(source) for source in source_results if source.executed)}", websocket)

            # if a source has succesfully executes add it's meta data to the consensus
            for source in source_results:
                if source.executed:
                    merge_variant_data(source, consensus_variant)
            
            # figure out the new consensus and check it
            await new_variant_from_consensus(consensus_variant, variant, search_variant, websocket) # type: ignore
            check_source_consensus(consensus_variant, variant, sources)
            
            # send all the logs and a source update to the client over the websocket connection
            for source in source_results:
                await send_logs(source.consume_logs(), websocket)
                if source.executed or source.timeout:
                    await send_source(source, websocket)
                if source.complete:
                    sources.remove(source)
            """ # probably not needed, 'if not source_results' is better check?
            if variant == previous_variant:
                await send_log(f"No new variant info this iteration, stopping", websocket)
                await send_consensus(consensus_variant, websocket)
                break
            """

            # hmm this is the same as on line 257
            if not source_results:
                await send_log(f"No sources queried this iteration, stopping", websocket)
                await send_consensus(consensus_variant, websocket)
                break
            
            # send the variant and consensus update to the client
            await send_variant(variant, websocket)
            await send_consensus(consensus_variant, websocket)

            if iteration >= max_iterations:
                await send_log(f"Reached max iterations: {iteration}/{max_iterations}, stopping", websocket)
                break
        
        # if there are still sources in the sources list, that means not all of them had enough meta data to run
        if sources:
            await send_log(f"Sources not completed: {', '.join([str(source) for source in sources])}", websocket)
        else:
            await send_log(f"Used all sources.", websocket)

    except WebSocketDisconnect:
        await websocket.close()

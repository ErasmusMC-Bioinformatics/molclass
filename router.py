import asyncio
from types import MappingProxyType
from typing import List

import aiohttp
from fastapi import APIRouter, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from icecream import ic

from database import SessionDep
from models import VariantData, VariantDataScheme, VariantSource

ic.configureOutput(prefix="debug-", includeContext=True)

from config import settings
from search import parse_search, parse_transcript
from sources.source_result import Source
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
        if not value:
            continue
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
async def websocket_endpoint(websocket: WebSocket, search: str, db_session: SessionDep):
    """
    The websocket that the client connects to, most of the server side work is handled from here
    """
    print(f"[DEBUG] WebSocket connection initiated for search: {search}")
    await websocket.accept()
    print("[DEBUG] WebSocket connection accepted")

    try:
        # it's probably impossible for molclass to get stuck querying sources for ever
        # but to be sure just cap it at something because why not
        iteration = 0
        max_iterations = 7

        variant = parse_search(search)
        ro_variant = MappingProxyType(variant)

        # wrap the search query meta data in a read only dict
        search_variant = MappingProxyType(dict(**variant))

        # holds the 'votes' for meta data values
        consensus_variant = {k: {v: ["search"]} for k, v in search_variant.items()}

        # init the active sources
        sources: List[Source] = [source(ro_variant, consensus_variant) for source in settings.sources]
        print(f"[DEBUG] Initialized {len(sources)} sources: {[str(s) for s in sources]}")

        await send_log(f"Starting with: {variant}", websocket)

        while True:
            iteration += 1
            print(f"[DEBUG] Starting iteration {iteration}/{max_iterations}")

            # set a total timout for all sources, so users don't end up waiting a long time for a slow source
            timeout = aiohttp.ClientTimeout(total=10)

            # optionally spoof our user agent to stop sources from complaining <.<
            # user_agent_header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0"}

            # the ClientSession is used by all sources for requests, allowing for async/await
            async with aiohttp.ClientSession(timeout=timeout, trust_env=True) as session:
                # gather all the current sources and prepare an asyncio task list
                tasks = []
                for source in sources:
                    tasks.append(asyncio.ensure_future(source.execute(session)))

                print(f"[DEBUG] Executing {len(tasks)} source tasks")
                # asynchronously execute all the source tasks
                source_results: List[Source] = await asyncio.gather(*tasks, return_exceptions=True)

                # Handle exceptions from gather
                valid_results = []
                for i, result in enumerate(source_results):
                    if isinstance(result, Exception):
                        print(f"[DEBUG] Source {sources[i]} failed with exception: {result}")
                        await send_log(f"Source {sources[i]} failed: {str(result)}", websocket)
                    else:
                        valid_results.append(result)
                source_results = valid_results

            # if a source is missing the required meta data it returns None, filter those out here
            source_results = [source_result for source_result in source_results if source_result]
            print(f"[DEBUG] Valid source results: {len(source_results)}")

            # if there are no source results we're done and can stop iterating
            if not source_results:
                print("[DEBUG] No source results, breaking loop")
                await send_log("No more sources to query, stopping", websocket)
                break
            else:
                executed_sources = [str(source) for source in source_results if source.executed]
                print(f"[DEBUG] Executed sources: {executed_sources}")
                await send_log(f"Iteration {iteration}, queried {', '.join(executed_sources)}", websocket)

            # if a source has successfully executed add its meta data to the consensus
            executed_count = 0
            for source in source_results:
                if source.executed:
                    executed_count += 1
                    merge_variant_data(source, consensus_variant)

            print(f"[DEBUG] {executed_count} sources executed successfully")

            # figure out the new consensus and check it
            await new_variant_from_consensus(consensus_variant, variant, search_variant, websocket)
            check_source_consensus(consensus_variant, variant, sources)

            # send all the logs and a source update to the client over the websocket connection
            completed_sources = []
            for source in source_results:
                await send_logs(source.consume_logs(), websocket)
                if source.executed or source.timeout:
                    await send_source(source, websocket)
                if source.complete:
                    completed_sources.append(source)
                    sources.remove(source)

            if completed_sources:
                print(f"[DEBUG] Completed and removed {len(completed_sources)} sources")

            # send the variant and consensus update to the client
            await send_variant(variant, websocket)
            await send_consensus(consensus_variant, websocket)

            if iteration >= max_iterations:
                print("[DEBUG] Reached max iterations limit")
                await send_log(f"Reached max iterations: {iteration}/{max_iterations}, stopping", websocket)
                break

        # if there are still sources in the sources list, that means not all of them had enough meta data to run
        if sources:
            incomplete_sources = [str(source) for source in sources]
            print(f"[DEBUG] Incomplete sources remaining: {incomplete_sources}")
            await send_log(f"Sources not completed: {', '.join(incomplete_sources)}", websocket)
        else:
            print("[DEBUG] All sources completed successfully")
            await send_log("Used all sources.", websocket)

        save_variant_normalized(search, consensus_variant, db_session)

    except WebSocketDisconnect:
        print("[DEBUG] WebSocket disconnected")
        await websocket.close()
    except Exception as e:
        print(f"[DEBUG] Unexpected error in websocket_endpoint: {e}")
        await send_log(f"Unexpected error occurred: {str(e)}", websocket)
        raise

def save_variant_normalized(search_term: str, consensus_variant: dict, session: SessionDep):
    variant_data = {}
    sources_data = []

    for field_name, field_dict in consensus_variant.items():
        if not field_dict or field_dict is None:
            continue

        # Get the first value as primary
        first_value = next(iter(field_dict.keys()))
        if first_value is not None:  # Only set if not None
            variant_data[map_field_name(field_name)] = first_value

        # Store all value-source combinations, skip None values
        for value, source_list in field_dict.items():
            if value is None:  # Skip None values
                continue
            for source in source_list:
                sources_data.append({
                    'field_name': field_name,
                    'field_value': str(value),  # Ensure string
                    'source_name': source
                })

    # Create variant record
    variant = VariantDataScheme(
        search_term=search_term,
        **variant_data
    )

    session.add(variant)
    session.flush()

    # Create source records (only non-None values)
    for source_data in sources_data:
        source = VariantSource(
            variant_id=variant.id,
            **source_data
        )
        session.add(source)

    session.commit()
    return variant.id

def map_field_name(consensus_field: str) -> str:
    """Map consensus_variant field names to database columns"""
    mapping = {
        'rs': 'rs_id',
        'to': 'to_pos',
        # Add other mappings as needed
    }
    return mapping.get(consensus_field, consensus_field)

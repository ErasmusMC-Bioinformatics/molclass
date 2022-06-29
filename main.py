from http.client import HTTPResponse
from fastapi import FastAPI, Request
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
    return templates.TemplateResponse(
        "index.html.jinja2", 
        {
            "request": request,
            "search": search,
            "sources": [source(variant) for source in settings.sources]
        }
    )

@app.get("/info")
def info():
    return settings.dict()


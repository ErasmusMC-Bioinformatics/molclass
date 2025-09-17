import logging.config
import multiprocessing
import os
from contextlib import asynccontextmanager

import uvicorn
import yaml
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from database import create_db_and_tables
from router import router
from util import relative_path

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

# only load the logging yaml if the file exists, mostly for pyinstaller
if os.path.exists(relative_path("logging.yaml")):
    with open(relative_path("logging.yaml")) as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
        logging.config.dictConfig(config)


app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory=relative_path("static")), name="static")

app.include_router(router)

if __name__ == "__main__":
    multiprocessing.freeze_support()
    uvicorn.run(app, host="0.0.0.0", workers=1, port=8080)
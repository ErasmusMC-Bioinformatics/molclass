import yaml
import uvicorn
import multiprocessing

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

import logging.config

from router import router

with open('logging.yaml') as f:
    config = yaml.load(f, Loader=yaml.FullLoader)
    logging.config.dictConfig(config)

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(router)

if __name__ == "__main__":
    multiprocessing.freeze_support()
    uvicorn.run(app, host="0.0.0.0", workers=1, port=8080)
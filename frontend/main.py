

import logging
import os
import random
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
from jinja2 import Template
from tempfile import TemporaryDirectory

logging.basicConfig(level=logging.INFO)

# TODO: move to .env or args
BACKEND = "http://localhost:8001"

app = FastAPI()




@app.get("/", response_class=HTMLResponse)
async def index():

    logging.info('Entry index')

    with open('web/index.html') as f:
        return Template(f.read()).render(BACKEND=BACKEND)


@app.get("/stream", response_class=HTMLResponse)
async def index():

    logging.info('Entry index')

    with open('web/stream.html') as f:
        return Template(f.read()).render(BACKEND=BACKEND)

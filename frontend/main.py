

import logging
import os
import random
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
from jinja2 import Template
from tempfile import TemporaryDirectory

logging.basicConfig(level=logging.INFO)

# TODO: move to .env or args
BACKEND = os.environ.get('BACKEND', "http://localhost:8004")
BACKEND_HTTPS = os.environ.get('BACKEND_HTTPS', "http://localhost:8084")

logging.info(f"Backend is: {BACKEND}")
logging.info(f"Backend_https is: {BACKEND_HTTPS}")

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def index():
    with open('web/index.html') as f:
        return Template(f.read()).render(BACKEND=BACKEND)

@app.get("/stream", response_class=HTMLResponse)
async def stream():
    with open('web/stream.html') as f:
        return Template(f.read()).render(BACKEND_HTTPS=BACKEND_HTTPS)

@app.get("/labels", response_class=HTMLResponse)
async def labels():
    with open('web/labels.html') as f:
        return Template(f.read()).render(BACKEND=BACKEND)
    
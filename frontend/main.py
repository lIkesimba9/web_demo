

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

with open('web/index.html') as f:
    index_template = Template(f.read())


@app.get("/", response_class=HTMLResponse)
async def index():

    logging.info('Entry index')

    content = index_template.render(BACKEND=BACKEND)
 
    return content
def sizeof_fmt(num, suffix="B"):
    for unit in ("", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"):
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"

# Mock
def find_regions(w, h, tmp_file_path):

    regions_count = random.randint(1, 5)

    regions = []

    for _ in range(regions_count):

        rand_w = random.randint(10, 100)
        rand_h = random.randint(10,  75)
        rand_x = random.randint(0, w - rand_w)
        rand_y = random.randint(0, h - rand_h)

        regions.append({
            'x':  rand_x, 'y':  rand_y, 'h': rand_h, 'w': rand_w
        })

    return regions  


@app.post("/process", response_class=JSONResponse)
async def process(file: UploadFile = File(...)):

    logging.info('Entry process')

    try:
        contents = file.file.read()

        with TemporaryDirectory() as tmp_dir:

            tmp_file_path = tmp_dir + '/' + file.filename

            logging.info(f"Start image uploaded to: {tmp_file_path}")

            with open(tmp_file_path, 'wb') as f:
                f.write(contents)

            logging.info(f"End upload")

            logging.info(f"Start processing")

            im = cv2.imread(tmp_file_path)

            h, w, c = im.shape

            # Mock
            regions = find_regions(w, h, tmp_file_path);

            return {'success': True,
                    'info': {'size': sizeof_fmt(os.path.getsize(tmp_file_path)),
                             'width': w,
                             'height': h,
                             'channel': c
                    },
                    'regions': regions
                    }

    except Exception as e:
        return {'success': False,
                "message": f"There was an error uploading the file: {e}"}

 

download model, and put to `./yolov8-triton/models/yolov8/1/model.onnx`

build docker
```bash
docker build -t yolov8-triton .
```
run docker

```bash
docker run --gpus all \
    -it --rm \
    --net=host \
    -v ./models:/models \
    yolov8-triton
```

api
```python
from ultralytics import YOLO

# Load the Triton Server model
model = YOLO(f"http://localhost:8000/yolov8", task="detect")

# Run inference on the server
results = model("path/to/image.jpg")

```

-------------------------------------------------

Build & run all services:

1. Download ML model, and put to `./web_demo/yolov8-triton/models/yolov8/1/model.onnx`
2. Create and put ```config``` folder (with ```auth.txt``` and ```credentials.ovpn```) to ```./web_demo/gemini_proxy```

3. Start services:
```
chmod +x start_services.sh
./start_services.sh <you_google_api_token>

```

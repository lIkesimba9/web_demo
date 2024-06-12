Create virtual enviroment for python
```
python3.7 -m venv venv
```

Activate virtual enviroment for python
```
source venv/bin/activate
```

Install dependencies
```
pip install -r requirements.txt
```

Run triton server in docker container
```
docker run -it --rm -p 8000:8000 -v ~/web_demo-main/yolov8-triton/models:/models yolov8-triton
```

Run python backend-server
```
python3 main.py
```

Run swagger in browser
```
Заходим в браузере: http://localhost:8001/docs
```

Enjoy

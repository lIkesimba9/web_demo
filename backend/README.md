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
docker run -it --rm -p 8000:8000 -v ~/web_demo-main/yolov8-triton/models:/models --name ml-service-container yolov8-triton
```

Run python backend-server OR Build docker & run it
```
python3 main.py
```
or
```
docker build -t ml-backend-python .
docker run --name ml-backend-container -p 8001:8001 ml-backend-python
```

Run swagger in browser
```
http://localhost:8001/docs
```

Notice:
For access to backend from frontend which runnning in docker-container need use hostname ```ml-backend-container``` instead ```localhost```

Enjoy

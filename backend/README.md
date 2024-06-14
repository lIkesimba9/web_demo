Install & run 'ollama' 
```
curl -fsSL https://ollama.com/install.sh | sh
ollama run llama3
```

Create virtual enviroment for python
```
python3.9 -m venv venv
```

Activate virtual enviroment for python
```
source venv/bin/activate
```

Install dependencies
```
python3.9 -m pip install -r requirements.txt
```

Run triton server in docker container
```
docker network create custom_network
docker run -it --rm -p 8000:8000 --network custom_network -v ./models:/models --name ml-service-container yolov8-triton
```

Run python backend-server OR Build docker & run it
```
python3.9 main.py
```
or
```
docker build -t ml-backend-python .
docker run --name ml-backend-container --network custom_network -p 8004:8004 ml-backend-python
```

Run swagger in browser
```
http://localhost:8004/docs
```

Notice:
For access to backend from frontend which runnning in docker-container need use hostname ```ml-backend-container``` instead ```localhost```

Enjoy

-------------------------------------------------------------------------------------

SIMPLE BUILD & RUN:

0. Install & run 'ollama' 
```
curl -fsSL https://ollama.com/install.sh | sh
ollama run llama3
```

1. From './web_demo/yolov8-triton' dir
```
docker build -t yolov8-triton .
docker network create custom_network
docker run -it --rm -p 8000:8000 --network custom_network -v ./models:/models --name ml-service-container yolov8-triton
```

2. Add '.env' file in './web_demo/backend' dir:
```
GOOGLE_API_KEY=<you_api_token>
```

3. From './web_demo/backend' dir:
```
docker build -t ml-backend-python .
docker run --name ml-backend-container --network custom_network -p 8004:8004 ml-backend-python
```

4. From browser:
```
http://localhost:8004/docs
```

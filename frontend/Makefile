create-env:
	python3 -m venv venv

update-reqs:
	venv/bin/pip install -r requirements.txt

run-demo-server:
	venv/bin/uvicorn main:app --host 0.0.0.0 --port 8010 --reload --reload-dir web --reload-include *.html

send-simple-file-with-curl:
	curl -i -X POST -H "Content-Type: multipart/form-data"  -F "file=@vidi-defectov-shvov.jpg" http://localhost:8001/process

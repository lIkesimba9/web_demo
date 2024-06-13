import os
import json
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, Form
from pydantic import BaseModel, conlist
from typing import List, Dict, Any
from ultralytics import YOLO
import torch


# YOLO Model Class
class YOLOModel:
    def __init__(self, name: str, size: str):
        # Temporary (!!!)
        if name == "yolov8" and size == "large":
            self.model = YOLO(f"http://ml-service-container:8000/{name}", task="detect")
        else:
            self.model = YOLO(f"http://ml-service-container:8000/{name}_{size}", task="detect")
        self.name = name
        self.size = size

    def infer(self, image_path: str):
        results = self.model(image_path)
        return results

# Request Schemas
class TrainingRequest(BaseModel):
    models: List[str]
    retrain: bool

# Response Schemas
class InferenceResult(BaseModel):
    results: Any

class BestResult(BaseModel):
    best_avarage_confidence: Dict[str, Any]
    best_inference_time: Dict[str, Any]
    intermediate_result: Any
    all_results: List[Dict[str, Any]]

class Label(BaseModel):
    coordinates: conlist(int, min_items=4, max_items=4)

class UploadLabeledImageRequest(BaseModel):
    labels: List[Label]

# FastAPI app
app = FastAPI()

# Helper function to calculate average results
def average_results(results):
    # Implement logic to calculate average results
    # pass
    return None # Как будем считать?

def file_exists(directory, filename):
    # Формируем полный путь к файлу
    file_path = os.path.join(directory, filename)
    # Проверяем, существует ли файл по этому пути
    return os.path.isfile(file_path)


def append_to_labels_file(directory, filename, labels):
    labels_file = os.path.join(directory, "labels.txt")
    coordinates_str = ", ".join([f"[{x1}, {y1}, {x2}, {y2}]" for (x1, y1, x2, y2) in labels])
    line = f"{filename} | [ {coordinates_str} ]\n"
    
    with open(labels_file, "a") as file:
        file.write(line)

def process_nn_results_coordinates(yolo_obj):
    result_array = []
    for i, box in enumerate(yolo_obj.boxes):
        x1, y1, x2, y2 = torch.round(box.xyxy.cpu()[0])
        single_arr = []
        x1 = int(x1.item())
        x2 = int(x2.item())
        y1 = int(y1.item())
        y2 = int(y2.item())
        single_arr.append(x1)
        single_arr.append(y1)
        single_arr.append(x2)
        single_arr.append(y2)
        result_array.append(single_arr)
    return result_array

def process_nn_result_conf(yolo_obj):
    result_array = []
    confidences = yolo_obj.boxes.conf
    for i, conf in enumerate(confidences):
        conv_val = conf.item()
        result_array.append(conv_val)
    return result_array

def calculate_average(arr):
    if len(arr) == 0:
        return 0
    return sum(arr) / len(arr)

@app.post("/infer", response_model=InferenceResult)
async def infer_image(model_name: str, model_size: str, file: UploadFile = File(...)):
    try:
        yolo_model = YOLOModel(model_name, model_size)
        image_path = f"temp/{file.filename}"
        with open(image_path, "wb") as image_file:
            image_file.write(file.file.read())
        results = yolo_model.infer(image_path)
        os.remove(image_path)
        yolo_obj = results[0]
        result_array = process_nn_results_coordinates(yolo_obj)
        return {"results": result_array}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/best_result", response_model=BestResult)
async def get_best_result(models: List[str], file: UploadFile = File(...)):
    try:
        image_path = f"temp/{file.filename}"
        with open(image_path, "wb") as image_file:
            image_file.write(file.file.read())

        results = []
        for model_info in models:
            model_name, model_size = model_info.split("_")
            yolo_model = YOLOModel(model_name, model_size)
            result = yolo_model.infer(image_path)
            yolo_obj = result[0]
            result_array_box = process_nn_results_coordinates(yolo_obj)
            result_confs = process_nn_result_conf(yolo_obj)
            results.append({"model": model_info, "result_array_box": result_array_box, "inference_time": yolo_obj.speed['inference'], "confidence": result_confs, "avarage_confidence": calculate_average(result_confs) })
        os.remove(image_path)
        
        best_avarage_confidence = max(results, key=lambda x: x["avarage_confidence"])
        best_inference_time = min(results, key=lambda x: x["inference_time"])

        return {
            "best_avarage_confidence": {"model_name/size": best_avarage_confidence["model"], "avarage_confidence": best_avarage_confidence["avarage_confidence"]} ,
            "best_inference_time": {"model_name/size": best_inference_time["model"], "inference_time": best_inference_time["inference_time"]},
            "intermediate_result": average_results(results),
            "all_results": results
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/upload_labeled_image")
async def upload_labeled_image(
    to_train: bool = Form(...), 
    labels: str = Form(...), 
    file: UploadFile = File(...)
):
    try:
        filename = file.filename
        path_to_image_dir = "images"
        while file_exists(path_to_image_dir, filename):
            filename += "_"
        image_path = f"{path_to_image_dir}/{filename}"

        with open(image_path, "wb") as image_file:
            image_file.write(file.file.read())

        # Parse the labels from the string input
        labels_list = json.loads(labels)
        append_to_labels_file(path_to_image_dir, filename, labels_list)
        
        return {"message": "Image uploaded and labeled successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/")
def read_root():
    return {"message": "Welcome to the ML Backend API"}

if __name__ == "__main__":
    import uvicorn
    dir1 = "images"
    dir2 = "temp"
    if not os.path.exists(dir1):
        os.makedirs(dir1)
    if not os.path.exists(dir2):
        os.makedirs(dir2)
    uvicorn.run(app, host="0.0.0.0", port=8001)

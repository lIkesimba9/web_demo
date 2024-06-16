import os
import json
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, Form
from pydantic import BaseModel, conlist
from typing import List, Dict, Any
from ultralytics import YOLO
import torch
from ollama import Client
import google.generativeai as genai
import requests
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import aiofiles
from concurrent.futures import ThreadPoolExecutor

classes_idx = {
    0 :'adj',
    1: 'int',
    2: 'geo',
    3: 'pro',
    4: 'non'
}

classes_descriptions = {
    'adj': "Прилегающие дефекты: брызги, прожоги от дуги",
    'int': "Дефекты целостности: кратер, шлак, свищ, пора, прожог, включения",
    'geo': "Дефекты геометрии: подрез, непровар, наплыв, чешуйчатость, западание, неравномерность",
    'pro': "Дефекты постобработки: заусенец, торец, задир, забоина",
    'non': "Дефекты невыполнения: незаполнение раковины, несплавление"
}

olama_client = Client(host='http://host.docker.internal:11434')
global_ml_models = None

executor = ThreadPoolExecutor()

class MLModelsInit:
    def __init__(self):
        global global_ml_models
        self.yolov8Model = YOLOModel("yolov8")
        global_ml_models = self

# YOLO Model Class
class YOLOModel:
    def __init__(self, name: str):
        self.model = YOLO(f"http://ml-service-container:8000/{name}", task="detect")
        self.name = name

    def infer(self, image_path: str):
        results = self.model(image_path)
        return results

# Init models
MLModelsInit()

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
app = FastAPI(
    title="API for working with machine learning models for object detection",
    description="This API provides capabilities for working with machine learning models designed for object detection. You can use it to recognize objects in images, upload tagged images, and get better recognition results from multiple neural networks",
    version="0.0.1"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def average_results(results):
    # Implement logic to calculate average results
    # pass
    return None

def file_exists(directory, filename):
    file_path = os.path.join(directory, filename)
    return os.path.isfile(file_path)

def append_to_labels_and_classes_file(directory, filename, labels, classes, descriptions):
    labels_file = os.path.join(directory, "labels.txt")
    coordinates_str = ", ".join([f"[{x1}, {y1}, {x2}, {y2}]" for (x1, y1, x2, y2) in labels])
    line = f"{filename} | [ {coordinates_str} ] | {classes} | {descriptions}\n"
    
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

def process_nn_result_class_names(yolo_obj):
    result_array = []
    classes = yolo_obj.boxes.cls.tolist()
    # names = yolo_obj.names
    for i, class_ in enumerate(classes):
        class_name = classes_idx[int(class_)]
        result_array.append(class_name)
    return result_array

def calculate_average(arr):
    if len(arr) == 0:
        return 0
    return sum(arr) / len(arr)

def get_description_based_on_class_name(model_text_AI_name, classes):
    try:
        request_string = "Тебе на вход будет передаваться описание дефекта сварного шва. Сгенерируй рекомендацию по устранению данного дефекта (ответ должен быть только на русском языке). Эти рекомендации могут носить как общий характер, так и углубленный с пояснением причин возникнованения данных дефектов и ошибок, допущенных сварщиком. Вот название дефекта: "
        responses = []
        for cls_ in classes:
            request_string_ = request_string + classes_descriptions[cls_]
            response = fetch_text_AI_chat_response(model_text_AI_name, request_string_)
            response_str = response["message"]["content"]
            responses.append(response_str)
        return responses
    except Exception as e:
        err_str = "Error getting response from 'text_AI'"
        print("Error:", err_str)
        return err_str

def fetch_text_AI_chat_response(model_text_AI_name, request_string):
    try:
        if model_text_AI_name == "llama3":
            response = olama_client.chat(model='llama3', messages=[
                {
                    'role': 'user',
                    'content': request_string,
                },
            ])
            print("response: ", response)
            return response
        # elif model_text_AI_name == "llama2":
        #     pass
        # etc
        else:
            raise ValueError("Unknown 'model_text_AI_name':", model_text_AI_name)
    except Exception as e:
        err_str = "Error getting response from 'text_AI'"
        print("Error:", err_str)
        return err_str

def call_text_image_AI_api(model_text_image_AI_name: str, text: str, file_path: str):
    api_url = "http://gemini_proxy:8005"
    url = f"{api_url}/text_image_AI"
    files = {'file': open(file_path, 'rb')}
    data = {'model_text_image_AI_name': model_text_image_AI_name, 'text': text}
    
    response = requests.post(url, data=data, files=files)
    
    if response.status_code == 200:
        result_str = response.json()["results"]
        print("result_str =", result_str)
        return result_str
    else:
        err_str = "Error getting response from 'text_image_AI'"
        print("Error:", err_str)
        return err_str

def string_to_list(string):
    try:
        # Преобразуем строку в список
        result = json.loads(string)
        return result
    except json.JSONDecodeError as e:
        return f"Ошибка при декодировании JSON: {e}"

def get_description_based_on_image(model_text_image_AI_name, image_path, result_array_box, classes):
    request_string = "Тебе на вход будет передаваться описания дефекта сварного шва. Координаты обнаруженного дефекта на изображении и само изображение. Сгенерируй рекомендацию по устранению данного дефекта (ответ должен быть только на русском языке). Эти рекомендации могут носить как общий характер, так и углубленный с пояснением причин возникнованения данных дефектов и ошибок, допущенных сварщиком."
    responses = []
    for cls_, coords in zip(classes,result_array_box):
        request_string_ = request_string + "Вот название/описание дефекта: " + classes_descriptions[cls_] + ". "
        request_string_ = request_string_ + "Вот координаты дефекта на изображении в формате xyxy: " + str(coords) + "."
        print("request_string_:", request_string_)
        response_str = call_text_image_AI_api(model_text_image_AI_name, request_string_, image_path)
        responses.append(response_str)
    return responses

async def save_upload_file(upload_file: UploadFile, destination: str):
    async with aiofiles.open(destination, 'wb') as out_file:
        while content := await upload_file.read(1024):
            await out_file.write(content)

async def remove_file(filepath: str):
    try:
        os.remove(filepath)
    except Exception as e:
        print(f"Error removing file {filepath}: {e}")

@app.post("/inference", response_model=InferenceResult, tags=["Inference"])
async def infer_image(model_name: str, model_text_AI_name: str, model_text_image_AI_name: str, run_AI_assistante: bool, file: UploadFile = File(...)):
    """
    API для детекции и классификации изображений с отображением времени "инференса", среднего значения confidence, а также возможностью получения пояснений от LLM моделей (text/text+image)
    """
    try:
        image_path = f"temp/{file.filename}"
        await save_upload_file(file, image_path)
        
        model = None
        results = None
        if model_name == "yolov8":
            event_loop = asyncio.get_event_loop()
            model = global_ml_models.yolov8Model
            results_ = model.infer(image_path)
            # results_ = await event_loop.run_in_executor(executor, model.infer, image_path)
            yolo_obj = results_[0]
            result_array_box = process_nn_results_coordinates(yolo_obj)
            classes = process_nn_result_class_names(yolo_obj)
            result_confs = process_nn_result_conf(yolo_obj)

            descriptions_based_on_class_names = "<no>"
            descriptions_based_on_image = "<no>"
            if run_AI_assistante:
                descriptions_based_on_class_names = await event_loop.run_in_executor(
                    executor, get_description_based_on_class_name, model_text_AI_name, classes)
                descriptions_based_on_image = await event_loop.run_in_executor(
                    executor, get_description_based_on_image, model_text_image_AI_name, image_path, result_array_box, classes)
                # descriptions_based_on_class_names = get_description_based_on_class_name(model_text_AI_name, classes)
                # descriptions_based_on_image = get_description_based_on_image(model_text_image_AI_name, image_path, result_array_box, classes)
            
            await remove_file(image_path)
            results = {
                "model": model_name,
                "result_array_box": result_array_box,
                "classes": classes,
                "inference_time": yolo_obj.speed['inference'],
                "confidence": result_confs,
                "avarage_confidence": calculate_average(result_confs),
                "descriptions_text_AI_model": descriptions_based_on_class_names,
                "descriptions_image_and_text_AI_model": descriptions_based_on_image
            }
        else:
            raise ValueError("Unknown 'model_name':", model_name)
        
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/few_networks_inference", response_model=BestResult, tags=["Inference"])
async def get_best_result(models: List[str], model_text_AI_name: str, model_text_image_AI_name: str, run_AI_assistante: bool, file: UploadFile = File(...)):
    """
    API для выполнения инференса на нескольких нейронных сетях, с выбиром лучших решений по качеству и по скорости инференса анализа
    """
    try:
        models = models[0].split(',')
        image_path = f"temp/{file.filename}"
        with open(image_path, "wb") as image_file:
            image_file.write(file.file.read())

        results = []
        for model_name in models:
            if model_name == "yolov8":
                model = global_ml_models.yolov8Model
                event_loop = asyncio.get_event_loop()
                results_ = model.infer(image_path)
                # results_ = await asyncio.get_event_loop().run_in_executor(executor, model.infer, image_path)
                yolo_obj = results_[0]
                result_array_box = process_nn_results_coordinates(yolo_obj)
                classes = process_nn_result_class_names(yolo_obj)
                result_confs = process_nn_result_conf(yolo_obj)
                descriptions_based_on_class_names = "<no>"
                descriptions_based_on_image = "<no>"
                if run_AI_assistante:
                    # descriptions_based_on_class_names = get_description_based_on_class_name(model_text_AI_name, classes)
                    # descriptions_based_on_image = get_description_based_on_image(model_text_image_AI_name, image_path, result_array_box, classes)
                    descriptions_based_on_class_names = await asyncio.get_event_loop().run_in_executor(
                        executor, get_description_based_on_class_name, model_text_AI_name, classes)
                    descriptions_based_on_image = await asyncio.get_event_loop().run_in_executor(
                        executor, get_description_based_on_image, model_text_image_AI_name, image_path, result_array_box, classes)
                results.append( 
                    {"model": model_name,
                     "result_array_box": result_array_box,
                     "classes": classes, 
                     "inference_time": yolo_obj.speed['inference'], 
                     "confidence": result_confs, 
                     "avarage_confidence": calculate_average(result_confs),
                     "descriptions_text_AI_model": descriptions_based_on_class_names, 
                     "descriptions_image_and_text_AI_model": descriptions_based_on_image 
                     }
                )
            # elif model_name == "yolov9":
            #     pass
            # etc
            else:
                raise ValueError("Unknown 'model_name':", model_name)
        os.remove(image_path)
        best_avarage_confidence = max(results, key=lambda x: x["avarage_confidence"])
        best_inference_time = min(results, key=lambda x: x["inference_time"])
        return {
            "best_avarage_confidence": {"model_name": best_avarage_confidence["model"], "avarage_confidence": best_avarage_confidence["avarage_confidence"]} ,
            "best_inference_time": {"model_name": best_inference_time["model"], "inference_time": best_inference_time["inference_time"]},
            "intermediate_result": average_results(results), # Пока заглушка
            "all_results": results
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/upload_labeled_image", tags=["Upload Labeled Image"])
async def upload_labeled_image(
    to_train: bool = Form(...), 
    labels: str = Form(...),
    classes: str = Form(...),
    descriptions: str = Form(...),
    file: UploadFile = File(...)
):
    """
    API для добавления новых изображений в выборку по мере их появления. При выявлении некорректных детекций и классификаций пользователи могут самостоятельно размечать изображения и добавлять пояснения.
    """
    try:
        filename = file.filename
        path_to_image_dir = "images"
        while file_exists(path_to_image_dir, filename):
            filename += "_"
        image_path = f"{path_to_image_dir}/{filename}"

        with open(image_path, "wb") as image_file:
            image_file.write(file.file.read())

        labels_list = json.loads(labels)
        append_to_labels_and_classes_file(path_to_image_dir, filename, labels_list, classes, descriptions)
        
        return {"message": "Image uploaded and labeled successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/", tags=["Greeting"])
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
    uvicorn.run(app, host="0.0.0.0", port=8004)
    # uvicorn.run(app, host="0.0.0.0", port=8004, ssl_keyfile="/certs/server.key", ssl_certfile="/certs/server.crt")

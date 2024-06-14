import os
import json
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, Form
from pydantic import BaseModel, conlist
from typing import List, Dict, Any
from dotenv import load_dotenv
import google.generativeai as genai


load_dotenv()

# openai_api_key = os.getenv('OPENAI_API_KEY')
google_api_key = os.getenv('GOOGLE_API_KEY')

# if not openai_api_key:
#     raise ValueError("OPENAI_API_KEY ключ не найден в .env файле")

if not google_api_key:
    raise ValueError("GOOGLE_API_KEY не найден в .env файле")

GOOGLE_API_KEY=google_api_key
genai.configure(api_key=GOOGLE_API_KEY)
gemai_model = genai.GenerativeModel('gemini-pro-vision')

# FastAPI app
app = FastAPI()

def fetch_text_image_AI_chat_response(model_text_image_AI_name, text, image_path_):
    try:
        if model_text_image_AI_name == "gemini-pro-vision":
            f = genai.upload_file(image_path_)
            response = gemai_model.generate_content([text, f])
            print(response)
            response_str = response.text
            return response_str
        elif model_text_image_AI_name == "chat-gpt-3.5":
            # model = global_ml_models.yolov8Model.infer()
            pass
        # и так далее
        else:
            raise ValueError("Unknown 'model_text_image_AI_name':", model_text_image_AI_name)

    except ValueError as ve:
        error_message = f"ValueError: {ve}"
        print(error_message)
        raise HTTPException(status_code=400, detail=error_message)
    except Exception as e:
        print("error_message:", print(e))
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/text_image_AI")
async def infer_gemini(model_text_image_AI_name: str = Form(...), text: str = Form(...), file: UploadFile = File(...)):
    try:
        image_path = f"temp/{file.filename}"
        with open(image_path, "wb") as image_file:
            image_file.write(file.file.read())
        results = fetch_text_image_AI_chat_response(model_text_image_AI_name, text, image_path)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    dir1 = "images"
    dir2 = "temp"
    if not os.path.exists(dir1):
        os.makedirs(dir1)
    if not os.path.exists(dir2):
        os.makedirs(dir2)
    uvicorn.run(app, host="0.0.0.0", port=8005)

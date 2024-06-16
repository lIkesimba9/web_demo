import requests

def call_gemini_api(model_text_image_AI_name: str, text: str, file_path: str):
    api_url = "http://localhost:8005"
    url = f"{api_url}/text_image_AI"
    files = {'file': open(file_path, 'rb')}
    data = {'model_text_image_AI_name': model_text_image_AI_name, 'text': text}
    
    response = requests.post(url, data=data, files=files)
    
    if response.status_code == 200:
        result_str = response.json()["results"]
        print("result_str =", result_str)
        return result_str
    else:
        raise Exception(f"Error {response.status_code}: {response.text}")

model_name = "gemini-pro-vision"
text_input = "Кто изображен на изображении?"
file_path = "1.png"

try:
    result = call_gemini_api(model_name, text_input, file_path)
    print("result", result)
except Exception as e:
    print(f"An error occurred: {e}")


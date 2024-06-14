import os
import aiohttp
from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from PIL import Image, ImageDraw, ImageFont
from telegram.constants import ParseMode
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
if not TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN не найден в .env файле")

INFERENCE_API_URL = 'http://ml-backend-container:8004/inference'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Привет! Отправьте мне изображение для анализа.')

async def call_inference_api(file_path: str):
    async with aiohttp.ClientSession() as session:
        with open(file_path, 'rb') as file:
            form = aiohttp.FormData()
            form.add_field('file', file, filename=os.path.basename(file_path))
            
            params = {
                'model_name': 'yolov8',
                'model_text_AI_name': 'llama3',
                'model_text_image_AI_name': 'gemini-pro-vision',
                'is_realtime': 'true'
            }
            
            async with session.post(INFERENCE_API_URL, data=form, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    response_text = await response.text()
                    raise Exception(f"API call failed with status {response.status}: {response_text}")

async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        photo = update.message.photo[-1]
        file = await photo.get_file()
        file_path = os.path.join('temp', file.file_id + '.jpg')
        await file.download(custom_path=file_path)
        print("[1]")
        # Вызов функции инференса
        inference_result = await call_inference_api(file_path)
        inference_result = inference_result["results"]
        print("[2]")
        print('inference_result:', inference_result)
        
        # inference_result = {
        #     'result_array_box': [[50, 50, 200, 200], [150, 150, 300, 300]], 
        #     'classes': ['cat', 'dog'], 
        #     'confidence': [0.85, 0.90],
        #     'avarage_confidence': 0.875,
        #     'inference_time': 0.123,
        #     'descriptions_text_AI_model': '<no>',
        #     'descriptions_image_and_text_AI_model': 'Cat and dog in the image'
        # }

        # Рисование прямоугольников на изображении
        image = Image.open(file_path)
        draw = ImageDraw.Draw(image)
        font = ImageFont.load_default()

        for box, cls, conf in zip(inference_result['result_array_box'], inference_result['classes'], inference_result['confidence']):
            draw.rectangle(box, outline='red', width=2)
            draw.text((box[0], box[1] - 10), f'{cls}', fill='red', font=font)
            draw.text((box[2], box[1] - 10), f'{conf:.2f}', fill='red', font=font)

        # Сохранение изображения с прямоугольниками
        result_image_path = os.path.join('temp', 'result_' + file.file_id + '.jpg')
        image.save(result_image_path)

        # Проверка существования файла перед отправкой
        if not os.path.exists(result_image_path):
            await update.message.reply_text('Не удалось создать файл с результатом.')
            return

        # Отправка изображения с подписью
        caption = (
            f"**Average confidence:** `{'{:.2f}'.format(inference_result['avarage_confidence'])}`\n"
            f"**Inference time:** `{'{:.3f}s'.format(inference_result['inference_time'])}`\n"
            f"**Descriptions Text AI Model:** `{'{}'.format(inference_result['descriptions_text_AI_model'])}`\n"
            f"**Descriptions Image and Text AI Model:** `{'{}'.format(inference_result['descriptions_image_and_text_AI_model'])}`"
        )
        
        with open(result_image_path, 'rb') as result_image_file:
            await update.message.reply_photo(photo=result_image_file, caption=caption, parse_mode=ParseMode.MARKDOWN_V2)

    except Exception as e:
        await update.message.reply_text(f'Ошибка: {e}')

def main():
    if not os.path.exists('temp'):
        os.makedirs('temp')

    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.PHOTO, handle_image))

    application.run_polling()

if __name__ == '__main__':
    main()

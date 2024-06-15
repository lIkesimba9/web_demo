import os
import aiohttp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from PIL import Image, ImageDraw, ImageFont
from telegram.constants import ParseMode
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
if not TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN не найден в .env файле")

INFERENCE_API_URL = 'http://ml-backend-container:8004/inference'

# Начальные параметры
default_params = {
    'model_name': 'yolov8',
    'model_text_AI_name': 'llama3',
    'model_text_image_AI_name': 'gemini-pro-vision',
    'run_AI_assistante': 'false',
    'confidence_threshold': 0.1,
    'line_thickness': 6,
    'line_color': 'blue',
    'class_font_size': 36,
    'class_font_color': 'blue',
    'confidence_font_size': 36,
    'confidence_font_color': 'blue'
}

# Словари для хранения параметров пользователей
user_params = {}

# Функция для получения параметров пользователя или использования значений по умолчанию
def get_user_params(user_id):
    if user_id not in user_params:
        user_params[user_id] = default_params.copy()
    return user_params[user_id]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("⚙️ Настройки", callback_data='settings')],
        [InlineKeyboardButton("📊 Показать текущие настройки", callback_data='show_params')],
        [InlineKeyboardButton("⚛️ Запустить анализ", callback_data='start_analysis')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Привет! Настройте параметры для анализа:', reply_markup=reply_markup)

async def show_main_menu(context, chat_id, text):
    keyboard = [
        [InlineKeyboardButton("⚙️ Настройки", callback_data='settings')],
        [InlineKeyboardButton("📊 Показать текущие настройки", callback_data='show_params')],
        [InlineKeyboardButton("⚛️ Запустить анализ", callback_data='start_analysis')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    params = get_user_params(user_id)

    if query.data == 'func_settings':
        keyboard = [
            [InlineKeyboardButton("🔍 Выбрать модель", callback_data='choose_model')],
            [InlineKeyboardButton("📚 Выбрать текстовую AI модель", callback_data='choose_text_ai')],
            [InlineKeyboardButton("🖼️ Выбрать модель текст+изображение AI", callback_data='choose_text_image_ai')],
            [InlineKeyboardButton("🤖 Выбрать режим работы (run AI assistents)", callback_data='choose_run_AI_assistents')],
            [InlineKeyboardButton("✅ Установить уровень confidence", callback_data='choose_confidence_threshold')],
            [InlineKeyboardButton("🔙 Назад", callback_data='settings')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text="Выберите параметры для анализа:", reply_markup=reply_markup)

    if query.data == 'view_settings':
        keyboard = [
            [InlineKeyboardButton("📏 Толщина линий", callback_data='choose_line_thickness')],
            [InlineKeyboardButton("🖊️ Цвет линий", callback_data='choose_line_color')],
            [InlineKeyboardButton("📝 Размер шрифта (class)", callback_data='choose_class_font_size')],
            [InlineKeyboardButton("🖍 Цвет шрифта (class)", callback_data='choose_class_font_color')],
            [InlineKeyboardButton("📝 Размер шрифта (confidence)", callback_data='choose_confidence_font_size')],
            [InlineKeyboardButton("🖍 Цвет шрифта (confidence)", callback_data='choose_confidence_font_color')],
            [InlineKeyboardButton("🔙 Назад", callback_data='settings')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text="Выберите параметры для анализа:", reply_markup=reply_markup)

    if query.data == 'settings':
        keyboard = [
            [InlineKeyboardButton("🛠 Функциональные настройки", callback_data='func_settings')],
            [InlineKeyboardButton("🌄 Настройки визуализации", callback_data='view_settings')],
            [InlineKeyboardButton("🔄 Сбросить параметры в default", callback_data='reset_defaults')],
            [InlineKeyboardButton("🔙 Назад", callback_data='back_to_main')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text="Выберите параметры для анализа:", reply_markup=reply_markup)

    elif query.data == 'back_to_main':
        keyboard = [
            [InlineKeyboardButton("⚙️ Настройки", callback_data='settings')],
            [InlineKeyboardButton("📊 Показать текущие настройки", callback_data='show_params')],
            [InlineKeyboardButton("⚛️ Запустить анализ", callback_data='start_analysis')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text="Настройте параметры для анализа:", reply_markup=reply_markup)

    elif query.data == 'reset_defaults':
        user_params[user_id] = default_params.copy()
        await query.edit_message_text(text="Параметры сброшены на значения по умолчанию.")
        await show_main_menu(context, query.message.chat_id, "Выберите дальнейшее действие")

    elif query.data == 'show_params':
        params_text = (
            f"**Текущие параметры:**\n"
            f"Модель: `{params['model_name']}`\n"
            f"Текстовая AI модель: `{params['model_text_AI_name']}`\n"
            f"Модель текст\+изображение AI: `{params['model_text_image_AI_name']}`\n"
            f"Режим работы \(run AI assistants\): `{params['run_AI_assistante']}`\n"
            f"Уровень confidence: `{params['confidence_threshold']}`\n"
            f"Толщина линий: `{params['line_thickness']}`\n"
            f"Цвет линий: `{params['line_color']}`\n"
            f"Размер шрифта \(класс\): `{params['class_font_size']}`\n"
            f"Цвет шрифта \(класс\): `{params['class_font_color']}`\n"
            f"Размер шрифта \(confidence\): `{params['confidence_font_size']}`\n"
            f"Цвет шрифта \(confidence\): `{params['confidence_font_color']}`"
        )
        await query.edit_message_text(text=params_text, parse_mode=ParseMode.MARKDOWN_V2)
        await show_main_menu(context, query.message.chat_id, "Выберите дальнейшее действие")


    elif query.data.startswith('choose_model'):
        keyboard = [
                [InlineKeyboardButton("yolov8", callback_data='model_yolov8')],
                [InlineKeyboardButton("resnet50", callback_data='model_resnet50')]
            ]
        await query.edit_message_text(text="Выберите модель:", reply_markup=InlineKeyboardMarkup(keyboard))
    elif query.data.startswith('model_'):
        model_name = query.data.split('_')[1]
        params['model_name'] = model_name
        await query.edit_message_text(text=f"Модель выбрана: {model_name}")
        await show_main_menu(context, query.message.chat_id, "Выберите дальнейшее действие")


    elif query.data.startswith('choose_text_ai'):
        keyboard = [
                [InlineKeyboardButton("llama3", callback_data='text_ai_llama3')],
                [InlineKeyboardButton("gpt3", callback_data='text_ai_gpt3')]
            ]
        await query.edit_message_text(text="Выберите текстовую AI модель:", reply_markup=InlineKeyboardMarkup(keyboard))
    elif query.data.startswith('text_ai_'):
        text_ai_name = query.data.split('_')[2]
        params['model_text_AI_name'] = text_ai_name
        await query.edit_message_text(text=f"Текстовая AI модель выбрана: {text_ai_name}")
        await show_main_menu(context, query.message.chat_id, "Выберите дальнейшее действие")

    elif query.data.startswith('choose_text_image_ai'):
        keyboard = [
                [InlineKeyboardButton("gemini-pro-vision", callback_data='text_image_ai_gemini')],
                [InlineKeyboardButton("clip", callback_data='text_image_ai_clip')]
            ]
        await query.edit_message_text(text="Выберите модель текст+изображение AI:", reply_markup=InlineKeyboardMarkup(keyboard))
    elif query.data.startswith('text_image_ai_'):
        text_image_ai_name = query.data.split('_')[3]
        params['model_text_image_AI_name'] = text_image_ai_name
        await query.edit_message_text(text=f"Модель текст+изображение AI выбрана: {text_image_ai_name}")
        await show_main_menu(context, query.message.chat_id, "Выберите дальнейшее действие")

    elif query.data.startswith('choose_run_AI_assistents'):
        keyboard = [
                [InlineKeyboardButton("true", callback_data='run_AI_assistents_true')],
                [InlineKeyboardButton("false", callback_data='run_AI_assistents_false')]
            ]
        await query.edit_message_text(text="Выберите режим работы (run AI assistants):", reply_markup=InlineKeyboardMarkup(keyboard))
    elif query.data.startswith('run_AI_assistents_'):
        run_AI_assistents = query.data.split('_')[3]
        params['run_AI_assistante'] = run_AI_assistents
        await query.edit_message_text(text=f"Режим работы (run AI assistants) выбран: {run_AI_assistents}")
        await show_main_menu(context, query.message.chat_id, "Выберите дальнейшее действие")

    elif query.data.startswith('choose_confidence_threshold'):
        keyboard = [
                [InlineKeyboardButton("0.3", callback_data='confidence_threshold_0.3')],
                [InlineKeyboardButton("0.5", callback_data='confidence_threshold_0.5')],
                [InlineKeyboardButton("0.7", callback_data='confidence_threshold_0.7')]
            ]
        await query.edit_message_text(text="Выберите уровень confidence:", reply_markup=InlineKeyboardMarkup(keyboard))
    elif query.data.startswith('confidence_threshold_'):
        confidence_threshold = float(query.data.split('_')[2])
        params['confidence_threshold'] = confidence_threshold
        await query.edit_message_text(text=f"Уровень confidence выбран: {confidence_threshold}")
        await show_main_menu(context, query.message.chat_id, "Выберите дальнейшее действие")

    elif query.data == 'start_analysis':
        await query.edit_message_text(text="Отправьте мне изображение для анализа.")

    elif query.data.startswith('choose_line_thickness'):
        keyboard = [
            [InlineKeyboardButton("1", callback_data='line_thickness_1')],
            [InlineKeyboardButton("2", callback_data='line_thickness_2')],
            [InlineKeyboardButton("3", callback_data='line_thickness_3')],
            [InlineKeyboardButton("4", callback_data='line_thickness_4')],
            [InlineKeyboardButton("5", callback_data='line_thickness_5')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text="Выберите толщину линий:", reply_markup=reply_markup)
        await show_main_menu(context, query.message.chat_id, 'Привет! Настройте параметры для анализа:')
    elif query.data.startswith('line_thickness_'):
        line_thickness = int(query.data.split('_')[2])
        params['line_thickness'] = line_thickness
        await query.edit_message_text(text=f"Толщина линий выбрана: {line_thickness}")
        await show_main_menu(context, query.message.chat_id, "Выберите дальнейшее действие")


    elif query.data.startswith('choose_line_color'):
        keyboard = [
            [InlineKeyboardButton("Красный", callback_data='line_color_red')],
            [InlineKeyboardButton("Зеленый", callback_data='line_color_green')],
            [InlineKeyboardButton("Синий", callback_data='line_color_blue')],
            [InlineKeyboardButton("Черный", callback_data='line_color_black')],
            [InlineKeyboardButton("Белый", callback_data='line_color_white')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text="Выберите цвет линий:", reply_markup=reply_markup)
    elif query.data.startswith('line_color_'):
        line_color = query.data.split('_')[2]
        params['line_color'] = line_color
        await query.edit_message_text(text=f"Цвет линий выбран: {line_color}")
        await show_main_menu(context, query.message.chat_id, "Выберите дальнейшее действие")

    elif query.data.startswith('choose_class_font_size'):
        keyboard = [
            [InlineKeyboardButton("10", callback_data='class_font_size_10')],
            [InlineKeyboardButton("12", callback_data='class_font_size_12')],
            [InlineKeyboardButton("14", callback_data='class_font_size_14')],
            [InlineKeyboardButton("16", callback_data='class_font_size_16')],
            [InlineKeyboardButton("18", callback_data='class_font_size_18')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text="Выберите размер шрифта (класс):", reply_markup=reply_markup)
    elif query.data.startswith('class_font_size_'):
        class_font_size = int(query.data.split('_')[3])
        params['class_font_size'] = class_font_size
        await query.edit_message_text(text=f"Размер шрифта (класс) выбран: {class_font_size}")
        await show_main_menu(context, query.message.chat_id, "Выберите дальнейшее действие")

    elif query.data.startswith('choose_class_font_color'):
        keyboard = [
            [InlineKeyboardButton("Красный", callback_data='class_font_color_red')],
            [InlineKeyboardButton("Зеленый", callback_data='class_font_color_green')],
            [InlineKeyboardButton("Синий", callback_data='class_font_color_blue')],
            [InlineKeyboardButton("Черный", callback_data='class_font_color_black')],
            [InlineKeyboardButton("Белый", callback_data='class_font_color_white')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text="Выберите цвет шрифта (класс):", reply_markup=reply_markup)
    elif query.data.startswith('class_font_color_'):
        class_font_color = query.data.split('_')[3]
        params['class_font_color'] = class_font_color
        await query.edit_message_text(text=f"Цвет шрифта (класс) выбран: {class_font_color}")
        await show_main_menu(context, query.message.chat_id, "Выберите дальнейшее действие")

    elif query.data.startswith('choose_confidence_font_size'):
        keyboard = [
            [InlineKeyboardButton("10", callback_data='confidence_font_size_10')],
            [InlineKeyboardButton("12", callback_data='confidence_font_size_12')],
            [InlineKeyboardButton("14", callback_data='confidence_font_size_14')],
            [InlineKeyboardButton("16", callback_data='confidence_font_size_16')],
            [InlineKeyboardButton("18", callback_data='confidence_font_size_18')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text="Выберите размер шрифта (confidence):", reply_markup=reply_markup)
    elif query.data.startswith('confidence_font_size_'):
        confidence_font_size = int(query.data.split('_')[3])
        params['confidence_font_size'] = confidence_font_size
        await query.edit_message_text(text=f"Размер шрифта (confidence) выбран: {confidence_font_size}")
        await show_main_menu(context, query.message.chat_id, "Выберите дальнейшее действие")

    elif query.data.startswith('choose_confidence_font_color'):
        keyboard = [
            [InlineKeyboardButton("Красный", callback_data='confidence_font_color_red')],
            [InlineKeyboardButton("Зеленый", callback_data='confidence_font_color_green')],
            [InlineKeyboardButton("Синий", callback_data='confidence_font_color_blue')],
            [InlineKeyboardButton("Черный", callback_data='confidence_font_color_black')],
            [InlineKeyboardButton("Белый", callback_data='confidence_font_color_white')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text="Выберите цвет шрифта (confidence):", reply_markup=reply_markup)
    elif query.data.startswith('confidence_font_color_'):
        confidence_font_color = query.data.split('_')[3]
        params['confidence_font_color'] = confidence_font_color
        await query.edit_message_text(text=f"Цвет шрифта (confidence) выбран: {confidence_font_color}")
        await show_main_menu(context, query.message.chat_id, "Выберите дальнейшее действие")

async def call_inference_api(file_path: str, params: dict):
    async with aiohttp.ClientSession() as session:
        with open(file_path, 'rb') as file:
            form = aiohttp.FormData()
            form.add_field('file', file, filename=os.path.basename(file_path))
            
            async with session.post(INFERENCE_API_URL, data=form, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    response_text = await response.text()
                    raise Exception(f"API call failed with status {response.status}: {response_text}")

async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.message.from_user.id
        params = get_user_params(user_id)

        if not params:
            await update.message.reply_text('Пожалуйста, настройте параметры перед отправкой изображения.')
            return

        await context.bot.send_message(chat_id=update.message.chat_id, text="Идет обработка изображения\.\.\.", parse_mode=ParseMode.MARKDOWN_V2)

        photo = update.message.photo[-1]
        file = await photo.get_file()
        file_path = os.path.join('temp', file.file_id + '.jpg')
        await file.download(custom_path=file_path)
        
        inference_result = await call_inference_api(file_path, params)
        inference_result = inference_result["results"]

        image = Image.open(file_path)
        draw = ImageDraw.Draw(image)
        font = ImageFont.load_default()
        confidence_font = ImageFont.load_default()

        for box, cls_, conf in zip(inference_result['result_array_box'], inference_result['classes'], inference_result['confidence']):
            if conf >= params['confidence_threshold']:
                draw.rectangle(box, outline=params['line_color'], width=params['line_thickness'])
                draw.text((box[0], box[1] - 10), f'{cls_}', fill=params['class_font_color'], font=font, anchor="ls", size=params['class_font_size'])
                draw.text((box[2], box[1] - 10), f'{conf:.2f}', fill=params['confidence_font_color'], font=confidence_font, anchor="ls", size=params['confidence_font_size'])

        # Сохранение изображения с прямоугольниками
        result_image_path = os.path.join('temp', 'result_' + file.file_id + '.jpg')
        image.save(result_image_path)

        # Проверка существования файла перед отправкой
        if not os.path.exists(result_image_path):
            await update.message.reply_text('Не удалось создать файл с результатом.')
            return

        # Отправка изображения с подписью
        caption = (
            f"**Average confidence:**  `{'{:.2f}'.format(inference_result['avarage_confidence'])}`\n"
            f"**Inference time:**      `{'{:.3f}s'.format(inference_result['inference_time'])}`\n"
        )

        AI_assistents_messages = (
            f"**Descriptions Text AI Model:** `{'{}'.format(inference_result['descriptions_text_AI_model'])}`\n\n"
            f"**Descriptions Image and Text AI Model:** `{'{}'.format(inference_result['descriptions_image_and_text_AI_model'])}`"
        )

        with open(result_image_path, 'rb') as result_image_file:
            await update.message.reply_photo(photo=result_image_file, caption=caption, parse_mode=ParseMode.MARKDOWN_V2)
        await context.bot.send_message(chat_id=update.message.chat_id, text=AI_assistents_messages, parse_mode=ParseMode.MARKDOWN_V2)
        await show_main_menu(context, update.message.chat_id, "Выберите дальнейшее действие")

    except Exception as e:
        await update.message.reply_text(f'Ошибка: {e}')

async def handle_image_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.message.from_user.id
        params = get_user_params(user_id)

        if not params:
            await update.message.reply_text('Пожалуйста, настройте параметры перед отправкой изображения.')
            return

        document = update.message.document
        if not document.mime_type.startswith('image/'):
            await update.message.reply_text('Пожалуйста, отправьте файл изображения.')
            return

        await context.bot.send_message(chat_id=update.message.chat_id, text="Идет обработка изображения\.\.\.", parse_mode=ParseMode.MARKDOWN_V2)

        file = await document.get_file()
        file_path = os.path.join('temp', file.file_id + os.path.splitext(document.file_name)[1])
        await file.download(custom_path=file_path)

        # Вызов функции инференса с параметрами пользователя
        inference_result = await call_inference_api(file_path, params)
        inference_result = inference_result["results"]

        # Рисование прямоугольников на изображении
        image = Image.open(file_path)
        draw = ImageDraw.Draw(image)
        font = ImageFont.load_default()  # Использование встроенного шрифта PIL
        confidence_font = ImageFont.load_default()

        for box, cls_, conf in zip(inference_result['result_array_box'], inference_result['classes'], inference_result['confidence']):
            if conf >= params['confidence_threshold']:
                draw.rectangle(box, outline=params['line_color'], width=params['line_thickness'])
                draw.text((box[0], box[1] - 10), f'{cls_}', fill=params['class_font_color'], font=font, anchor="ls", size=params['class_font_size'])
                draw.text((box[2], box[1] - 10), f'{conf:.2f}', fill=params['confidence_font_color'], font=confidence_font, anchor="ls", size=params['confidence_font_size'])

        # Сохранение изображения с прямоугольниками
        result_image_path = os.path.join('temp', 'result_' + file.file_id + '.jpg')
        image.save(result_image_path)

        if not os.path.exists(result_image_path):
            await update.message.reply_text('Не удалось создать файл с результатом.')
            return

        caption = (
            f"**Average confidence:**  `{'{:.2f}'.format(inference_result['avarage_confidence'])}`\n"
            f"**Inference time:**      `{'{:.3f}s'.format(inference_result['inference_time'])}`\n"
        )

        AI_assistents_messages = (
            f"**Descriptions Text AI Model:** `{'{}'.format(inference_result['descriptions_text_AI_model'])}`\n\n"
            f"**Descriptions Image and Text AI Model:** `{'{}'.format(inference_result['descriptions_image_and_text_AI_model'])}`"
        )

        with open(result_image_path, 'rb') as result_image_file:
            await update.message.reply_photo(photo=result_image_file, caption=caption, parse_mode=ParseMode.MARKDOWN_V2)
        await context.bot.send_message(chat_id=update.message.chat_id, text=AI_assistents_messages, parse_mode=ParseMode.MARKDOWN_V2)
        await show_main_menu(context, update.message.chat_id, "Выберите дальнейшее действие")

    except Exception as e:
        await update.message.reply_text(f'Ошибка: {e}')

def main():
    if not os.path.exists('temp'):
        os.makedirs('temp')

    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.PHOTO, handle_image))
    application.add_handler(MessageHandler(filters.Document.IMAGE, handle_image_file))

    application.run_polling()

if __name__ == '__main__':
    main()

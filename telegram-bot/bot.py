import os
import aiohttp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from PIL import Image, ImageDraw, ImageFont
from telegram.constants import ParseMode
from dotenv import load_dotenv
import cv2
import asyncio

load_dotenv()
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
if not TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN не найден в .env файле")

INFERENCE_API_URL = 'http://ml-backend-container:8004/inference'

classes_colors = {
    'adj': (255, 0, 0),
    'int': (255, 255, 0),
    'geo': (0, 234, 255),
    'pro': (170, 0, 255),
    'non': (255, 127, 0)
}

def get_color_code(color_name):
    colors = {
        "red": (0, 0, 255),
        "green": (0, 255, 0),
        "blue": (255, 0, 0),
        "yellow": (0, 255, 255),
        "cyan": (255, 255, 0),
        "magenta": (255, 0, 255),
        "white": (255, 255, 255),
        "black": (0, 0, 0),
        "gray": (128, 128, 128)
    }
    return colors.get(color_name.lower(), (0, 0, 0))

# Начальные параметры
default_params = {
    'model_name': 'yolov8',
    'model_text_AI_name': 'gpt3',
    'model_text_image_AI_name': 'gemini-pro-vision',
    'run_AI_assistante': 'false',
    'confidence_threshold': 0.1,
    'line_thickness': 6,
    'line_color': 'blue',
    'use_diff_color_for_diff_classes': 'true',
    'show_box_info': 'true',
    'class_font_scale': "0.9",
    'class_font_color': 'blue',
    'confidence_font_scale': "0.9",
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
        [InlineKeyboardButton("⚙️ Настройки", callback_data='settings')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    # await update.message.reply_text('Это телеграм\-бот `ML bot` проекта __VisionAI Suite__\. \n\nЧтобы начать пользоваться `ML bot` просто отправьте ему изображение для анализа\.\n\nДля гибкой конфигурирования `ML bot` перейдите\nв раздел `⚙️ Настройки`', reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN_V2)
    await update.message.reply_text('Телеграм\-бот ML bot разработан в рамках решения задачи «Определение и классификация дефектов сварных швов с помощью ИИ» на Атомик Хак 2\.0\n\n***Чтобы начать пользоваться ML bot просто отправьте ему изображение\.***\n\nДля настройки ML bot может перейти в раздел ⚙️ Настройки', reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN_V2)

async def show_main_menu(context, chat_id, text):
    keyboard = [
        [InlineKeyboardButton("⚙️ Настройки", callback_data='settings')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN_V2)

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
            [InlineKeyboardButton("🔙 Назад", callback_data='settings')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text="Выберите конфигурационные параметры:", reply_markup=reply_markup)

    if query.data == 'view_settings':
        keyboard = [
            [InlineKeyboardButton("✅ Нижняя граница уверенности", callback_data='choose_confidence_threshold')],
            [InlineKeyboardButton("📏 Толщина линий", callback_data='choose_line_thickness')],
            [InlineKeyboardButton("🖊️ Цвет линий", callback_data='choose_line_color')],
            [InlineKeyboardButton("🎨 Разные цвета для классов", callback_data='choose_diff_color')],
            [InlineKeyboardButton("🔬 Отображать классы и точность", callback_data='choose_show_box_info')],
            [InlineKeyboardButton("📝 Размер шрифта (класс)", callback_data='choose_class_font_scale')],
            [InlineKeyboardButton("🖍 Цвет шрифта (класс)", callback_data='choose_class_font_color')],
            [InlineKeyboardButton("📝 Размер шрифта (уверенность)", callback_data='choose_confidence_font_scale')],
            [InlineKeyboardButton("🖍 Цвет шрифта (уверенность)", callback_data='choose_confidence_font_color')],
            [InlineKeyboardButton("🔙 Назад", callback_data='settings')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text="Выберите конфигурационные параметры:", reply_markup=reply_markup)

    if query.data == 'settings':
        keyboard = [
            [InlineKeyboardButton("🛠 Расширенные настройки", callback_data='func_settings')],
            [InlineKeyboardButton("🌄 Настройки визуализации", callback_data='view_settings')],
            [InlineKeyboardButton("📊 Показать текущие настройки", callback_data='show_params')],
            [InlineKeyboardButton("🔄 Применить параметры по умолчанию", callback_data='reset_defaults')],
            [InlineKeyboardButton("🔙 Назад", callback_data='back_to_main')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text="Выберите конфигурационные параметры:", reply_markup=reply_markup)

    elif query.data == 'back_to_main':
        keyboard = [
            [InlineKeyboardButton("⚙️ Настройки", callback_data='settings')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text="_Можете загружать очередное изображение_", reply_markup=reply_markup)

    elif query.data == 'reset_defaults':
        user_params[user_id] = default_params.copy()
        await query.edit_message_text(text="Параметры сброшены до значений по умолчанию.")
        await show_main_menu(context, query.message.chat_id, "_Можете загружать очередное изображение_")

    elif query.data == 'show_params':
        params_text = (
            f"__Текущие параметры:__\n"
            f"Модель: `{params['model_name']}`\n"
            f"Текстовая AI модель: `{params['model_text_AI_name']}`\n"
            f"Модель текст\+изображение AI: `{params['model_text_image_AI_name']}`\n"
            f"Режим работы \(run AI assistents\): `{params['run_AI_assistante']}`\n"
            f"Уровень уверенности: `{params['confidence_threshold']}`\n"
            f"Толщина линий: `{params['line_thickness']}`\n"
            f"Цвет линий: `{params['line_color']}`\n"
            f"Разные цвета для классов: `{params['use_diff_color_for_diff_classes']}`\n"
            f"Отображение классов и уверенности: `{params['show_box_info']}`\n"
            f"Размер шрифта \(класс\): `{params['class_font_scale']}`\n"
            f"Цвет шрифта \(класс\): `{params['class_font_color']}`\n"
            f"Размер шрифта \(уверенность\): `{params['confidence_font_scale']}`\n"
            f"Цвет шрифта \(уверенность\): `{params['confidence_font_color']}`"
        )
        await query.edit_message_text(text=params_text, parse_mode=ParseMode.MARKDOWN_V2)
        await show_main_menu(context, query.message.chat_id, "_Можете загружать очередное изображение_")


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
        await show_main_menu(context, query.message.chat_id, "_Можете загружать очередное изображение_")


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
        await show_main_menu(context, query.message.chat_id, "_Можете загружать очередное изображение_")

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
        await show_main_menu(context, query.message.chat_id, "_Можете загружать очередное изображение_")

    elif query.data.startswith('choose_run_AI_assistents'):
        keyboard = [
                [InlineKeyboardButton("Да", callback_data='run_AI_assistents_true')],
                [InlineKeyboardButton("Нет", callback_data='run_AI_assistents_false')]
            ]
        await query.edit_message_text(text="Выберите режим работы (run AI assistants):", reply_markup=InlineKeyboardMarkup(keyboard))
    elif query.data.startswith('run_AI_assistents_'):
        run_AI_assistents = query.data.split('_')[3]
        params['run_AI_assistante'] = run_AI_assistents
        await query.edit_message_text(text=f"Режим работы (run AI assistants) выбран: {run_AI_assistents}")
        await show_main_menu(context, query.message.chat_id, "_Можете загружать очередное изображение_")

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
        await show_main_menu(context, query.message.chat_id, "_Можете загружать очередное изображение_")


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
        await show_main_menu(context, query.message.chat_id, "_Можете загружать очередное изображение_")

    elif query.data.startswith('choose_diff_color'):
        keyboard = [
            [InlineKeyboardButton("Да", callback_data='diff_color_true')],
            [InlineKeyboardButton("Нет", callback_data='diff_color_false')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text="Использовать разные цвета для классов:", reply_markup=reply_markup)
    elif query.data.startswith('diff_color_'):
        diff_color = query.data.split('_')[2]
        params['use_diff_color_for_diff_classes'] = diff_color
        await query.edit_message_text(text=f"Использовать разные цвета для классов: {diff_color}")
        await show_main_menu(context, query.message.chat_id, "_Можете загружать очередное изображение_")

    elif query.data.startswith('choose_show_box_info'):
        keyboard = [
            [InlineKeyboardButton("Да", callback_data='show_box_info_true')],
            [InlineKeyboardButton("Нет", callback_data='show_box_info_false')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text="Отображать классы и точность:", reply_markup=reply_markup)
    elif query.data.startswith('show_box_info_'):
        show_box_info = query.data.split('_')[3]
        params['show_box_info'] = show_box_info
        await query.edit_message_text(text=f"Отображать классы и точность: {show_box_info}")
        await show_main_menu(context, query.message.chat_id, "_Можете загружать очередное изображение_")

    elif query.data.startswith('choose_class_font_scale'):
        keyboard = [
            [InlineKeyboardButton("0.2", callback_data='class_font_scale_0.2')],
            [InlineKeyboardButton("0.4", callback_data='class_font_scale_0.4')],
            [InlineKeyboardButton("0.6", callback_data='class_font_scale_0.6')],
            [InlineKeyboardButton("0.8", callback_data='class_font_scale_0.8')],
            [InlineKeyboardButton("1.0", callback_data='class_font_scale_1.0')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text="Выберите размер шрифта (класс):", reply_markup=reply_markup)
    elif query.data.startswith('class_font_scale_'):
        class_font_scale = float(query.data.split('_')[3])
        params['class_font_scale'] = class_font_scale
        await query.edit_message_text(text=f"Размер шрифта (класс) выбран: {class_font_scale}")
        await show_main_menu(context, query.message.chat_id, "_Можете загружать очередное изображение_")

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
        await show_main_menu(context, query.message.chat_id, "_Можете загружать очередное изображение_")

    elif query.data.startswith('choose_confidence_font_scale'):
        keyboard = [
            [InlineKeyboardButton("0.2", callback_data='confidence_font_scale_0.2')],
            [InlineKeyboardButton("0.4", callback_data='confidence_font_scale_0.4')],
            [InlineKeyboardButton("0.6", callback_data='confidence_font_scale_0.6')],
            [InlineKeyboardButton("0.8", callback_data='confidence_font_scale_0.8')],
            [InlineKeyboardButton("1.0", callback_data='confidence_font_scale_1.0')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text="Выберите размер шрифта (уверенность):", reply_markup=reply_markup)
    elif query.data.startswith('confidence_font_scale_'):
        confidence_font_scale = float(query.data.split('_')[3])
        params['confidence_font_scale'] = confidence_font_scale
        await query.edit_message_text(text=f"Размер шрифта (уверенность) выбран: {confidence_font_scale}")
        await show_main_menu(context, query.message.chat_id, "_Можете загружать очередное изображение_")

    elif query.data.startswith('choose_confidence_font_color'):
        keyboard = [
            [InlineKeyboardButton("Красный", callback_data='confidence_font_color_red')],
            [InlineKeyboardButton("Зеленый", callback_data='confidence_font_color_green')],
            [InlineKeyboardButton("Синий", callback_data='confidence_font_color_blue')],
            [InlineKeyboardButton("Черный", callback_data='confidence_font_color_black')],
            [InlineKeyboardButton("Белый", callback_data='confidence_font_color_white')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text="Выберите цвет шрифта (уверенность):", reply_markup=reply_markup)
    elif query.data.startswith('confidence_font_color_'):
        confidence_font_color = query.data.split('_')[3]
        params['confidence_font_color'] = confidence_font_color
        await query.edit_message_text(text=f"Цвет шрифта (уверенность) выбран: {confidence_font_color}")
        await show_main_menu(context, query.message.chat_id, "_Можете загружать очередное изображение_")

async def call_inference_api(file_path: str, params: dict):
    async with aiohttp.ClientSession() as session:
        with open(file_path, 'rb') as file:
            form = aiohttp.FormData()
            form.add_field('file', file, filename=os.path.basename(file_path))
            
            async with session.post(INFERENCE_API_URL, data=form, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_response = await response.json()
                    response_text = error_response.get("detail", str(error_response))
                    raise Exception(f"API call failed with status {response.status}: {response_text}")

async def process_image_and_send(file_path, params, file_id, update, context):
    try:
        inference_result = await call_inference_api(file_path, params)
        inference_result = inference_result["results"]

        img = cv2.imread(file_path)

        for box, cls_, conf in zip(inference_result['result_array_box'], inference_result['classes'], inference_result['confidence']):
            if conf >= params['confidence_threshold']:
                line_color_code = None
                if params['use_diff_color_for_diff_classes'] == "true":
                    line_color_code = classes_colors[cls_]
                else:
                    line_color_code = get_color_code(params['line_color'])
                img = cv2.rectangle(img, (box[0], box[1]), (box[2], box[3]), line_color_code, int(params['line_thickness']))
                font_color_code_class = get_color_code(params['class_font_color'])
                font_color_code_conf = get_color_code(params['confidence_font_color'])
                font_scale_class = params['class_font_scale']
                font_scale_conf = params['confidence_font_scale']
                if params['show_box_info'] == "true":
                    cv2.putText(img, cls_, (box[0], box[1]-15), cv2.FONT_HERSHEY_SIMPLEX, float(font_scale_class), font_color_code_class, int(params['line_thickness']))
                    cv2.putText(img, f"{conf:.2f}", (box[2], box[1]-15), cv2.FONT_HERSHEY_SIMPLEX, float(font_scale_conf), font_color_code_conf, int(params['line_thickness']))

        result_image_path = os.path.join('temp', 'result_' + file_id + '.jpg')
        cv2.imwrite(result_image_path, img)

        if not os.path.exists(result_image_path):
            await update.message.reply_text('Не удалось создать файл с результатом.')
            return

        caption = (
            f"***Average confidence:***  `{'{:.2f}'.format(inference_result['avarage_confidence'])}`\n"
            f"***Inference time:***           `{'{:.3f} ms'.format(inference_result['inference_time'])}`\n"
        )

        AI_assistents_messages = (
            f"***Descriptions Text AI Model:***\n`{'{}'.format(inference_result['descriptions_text_AI_model'])}`\n\n"
            f"***Descriptions Image and Text AI Model:***\n`{'{}'.format(inference_result['descriptions_image_and_text_AI_model'])}`"
        )

        with open(result_image_path, 'rb') as result_image_file:
            await update.message.reply_photo(photo=result_image_file, caption=caption, parse_mode=ParseMode.MARKDOWN_V2)
        await context.bot.send_message(chat_id=update.message.chat_id, text=AI_assistents_messages, parse_mode=ParseMode.MARKDOWN_V2)
        await show_main_menu(context, update.message.chat_id, "_Можете загружать очередное изображение_")
    except Exception as e:
        await update.message.reply_text(f'Ошибка: {e}')
        await show_main_menu(context, update.message.chat_id, "_Можете загружать очередное изображение_")

async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.message.from_user.id
        params = get_user_params(user_id)

        if not params:
            await update.message.reply_text('Пожалуйста, настройте параметры перед отправкой изображения\.')
            return

        await context.bot.send_message(chat_id=update.message.chat_id, text="Идет обработка изображения\.\.\.", parse_mode=ParseMode.MARKDOWN_V2)

        photo = update.message.photo[-1]
        file = await photo.get_file()
        file_path = os.path.join('temp', file.file_id + '.jpg')
        await file.download(custom_path=file_path)
        asyncio.create_task(process_image_and_send(file_path, params, file.file_id, update, context))

    except Exception as e:
        await update.message.reply_text(f'Ошибка: {e}')
        await show_main_menu(context, update.message.chat_id, "_Можете загружать очередное изображение_")

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
        asyncio.create_task(process_image_and_send(file_path, params, file.file_id, update, context))
        
    except Exception as e:
        await update.message.reply_text(f'Ошибка: {e}')
        await show_main_menu(context, update.message.chat_id, "_Можете загружать очередное изображение_")

def main():
    if not os.path.exists('temp'):
        os.makedirs('temp')

    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.PHOTO, handle_image))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_image_file)) #IMAGE

    application.run_polling()

if __name__ == '__main__':
    main()

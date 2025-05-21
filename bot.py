import io
import logging
import pytesseract
import telebot
import torch
from PIL import Image
from pix2tex.cli import LatexOCR
from config import TOKEN

# Настройка модели LaTeX OCR
device = "cuda" if torch.cuda.is_available() else "cpu"
latex_model = LatexOCR()

# Логирование
logging.basicConfig(
    filename='bot.log',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Инициализация бота
bot = telebot.TeleBot(TOKEN)

def process_image(image: Image.Image, lang):
    logger.info("Пробуем обычное OCR...")
    text = pytesseract.image_to_string(image, lang=lang, config='--psm 3')
    return text, 'text'

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "Привет! Отправьте мне фото с текстом, а я постараюсь его распознать."
    )

@bot.message_handler(commands=['help'])
def help_message(message):
    bot.send_message(
        message.chat.id,
        "Доступные команды:\n"
        "/start – начать\n"
        "/help – помощь\n"
        "Просто отправьте фото, и я попробую распознать текст."
    )

@bot.message_handler(content_types=['photo'])
def photo_handler(message):
    bot.send_chat_action(message.chat.id, 'typing')
    bot.send_message(message.chat.id, "Фото получено, начинаю обработку...")
    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        image = Image.open(io.BytesIO(downloaded_file)).convert('RGB')
        lang = 'eng+rus'
        result = process_image(image, lang)
        bot.send_message(message.chat.id, result or "Не удалось распознать текст.")
    except Exception as e:
        logger.error(f"Ошибка при обработке фото: {e}")
        bot.send_message(message.chat.id, "Ошибка при обработке фото.")

@bot.message_handler(content_types=['document'])
def document_handler(message):
    if message.document.file_name.lower().endswith(('.png', '.jpg', '.jpeg')):
        bot.send_chat_action(message.chat.id, 'typing')
        bot.send_message(message.chat.id, "Получен документ, обрабатываю как изображение...")
        try:
            file_info = bot.get_file(message.document.file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            image = Image.open(io.BytesIO(downloaded_file)).convert('RGB')
            lang = 'eng+rus'
            result, mode = process_image(image, lang)
            bot.send_message(message.chat.id, result or "Не удалось распознать текст.")
        except Exception as e:
            logger.error(f"Ошибка при обработке документа: {e}")
            bot.send_message(message.chat.id, f"Не удалось обработать документ: {e}")

bot.polling(none_stop=True)
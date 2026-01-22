import logging
from pathlib import Path
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes
from telegram.constants import ParseMode
from md2tgmd import escape

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Токен бота
BOT_TOKEN = "8517102875:AAGTljF0sIeIr2a1JT_gyLvrD2LHKqU4I5c"
ALLOWED_USER_ID = 3153143


async def plans_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /plans"""
    if update.message.from_user.id != ALLOWED_USER_ID:
        return
    
    logger.info(f"Received /plans command from chat {update.effective_chat.id}")
    await send_markdown_file(update, context, "plans.md")


async def strategy_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /strategy"""
    if update.message.from_user.id != ALLOWED_USER_ID:
        return
    
    logger.info(f"Received /strategy command from chat {update.effective_chat.id}")
    await send_markdown_file(update, context, "strategy.md")


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик всех сообщений в группах"""
    if update.message.from_user.id != ALLOWED_USER_ID:
        return
    
    # Проверяем, что сообщение из группы
    if update.effective_chat.type not in ["group", "supergroup"]:
        return
    
    # Создаем имя файла на основе ID группы
    chat_id = abs(update.effective_chat.id)
    filename = f"{chat_id}_tasks.txt"
    
    # Записываем сообщение в файл
    try:
        with open(filename, "a", encoding="utf-8") as f:
            f.write(f"- {update.message.text}\n")
        logger.info(f"Saved message to {filename}")
    except Exception as e:
        logger.error(f"Error writing to file: {e}")


async def send_markdown_file(update: Update, context: ContextTypes.DEFAULT_TYPE, filename: str):
    """Отправляет содержимое markdown файла в чат"""
    try:
        # Читаем файл
        content = Path(filename).read_text(encoding="utf-8")
        logger.info(f"Successfully read {filename}, length: {len(content)} bytes")
        
        # Конвертируем markdown в Telegram entities
        telegram_content = escape(content)
        logger.info(f"Converted content:\n{telegram_content}")
        
        # Отправляем сообщение
        await update.message.reply_text(
            telegram_content,
            parse_mode=ParseMode.MARKDOWN_V2
        )
        logger.info("Message sent successfully")
        
    except FileNotFoundError:
        logger.error(f"Error reading {filename}: File not found")
        await update.message.reply_text(f"Error reading {filename} file")
    except Exception as e:
        logger.error(f"ERROR sending message: {e}")
        # Пробуем отправить как обычный текст
        try:
            logger.info("Trying to send as plain text...")
            await update.message.reply_text(content)
            logger.info("Plain message sent successfully")
        except Exception as e2:
            logger.error(f"ERROR sending plain message: {e2}")


def main():
    """Главная функция"""
    # Создаем приложение бота
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Регистрируем обработчики
    application.add_handler(CommandHandler("plans", plans_command))
    application.add_handler(CommandHandler("strategy", strategy_command))
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND & (filters.ChatType.GROUP | filters.ChatType.SUPERGROUP),
        message_handler
    ))
    
    logger.info("Bot started")
    
    # Запускаем бота
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()

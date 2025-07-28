import logging

from asgiref.sync import sync_to_async
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, BotCommand, BotCommand
from telegram.ext import Application, CommandHandler, ContextTypes, filters, ConversationHandler, MessageHandler

from app.settings import TELEGRAM_BOT_TOKEN
from app.telegram_bot.handlers import setup_handlers
from app.telegram_bot.models import TgUser

logger = logging.getLogger(__name__)

COMMANDS = [
    BotCommand('start', 'Запустить бота'),
    BotCommand('subscribe', 'Подписаться на рассылку'),
    BotCommand('show_settings', 'Мои настройки фильтра'),
    BotCommand('settings', 'Настроить фильтры'),
]

async def set_commands(application):
    await application.bot.set_my_commands(COMMANDS)

def run_bot():
    logger.info('Starting telegram bot')    
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    setup_handlers(application)
    application.post_init = set_commands
    logger.info('running bot')
    application.run_polling()
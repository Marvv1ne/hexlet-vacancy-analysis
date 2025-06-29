import logging

from asgiref.sync import sync_to_async
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, BotCommand, Bot
from telegram.ext import Application, CommandHandler, ContextTypes, filters, ConversationHandler, MessageHandler

from app.settings import TELEGRAM_BOT_TOKEN
from app.telegram_bot.models import TgUser
from app.telegram_bot.handlers import setup_handlers

logger = logging.getLogger('django')

COMMANDS = [
    BotCommand('start', 'Запустить бота'),
    BotCommand('subscribe', 'Подписаться на рассылку'),
    BotCommand('subscribe_to_vacancies', 'Подписаться на вакансии'),
    BotCommand('my_subscribes', 'Мои подписки'),
    BotCommand('settings', 'Настроить фильтры'),
    BotCommand('loads', 'Выгрузить вакансии'),
]

async def set_commands(application):
    await application.bot.set_my_commands(COMMANDS)

# Commands

def run_bot():
    '''Main function for start telegram bot'''
    logger.info('starting managment command')
    
    
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    
    setup_handlers(application)
    # Устанавливаем команды
    application.post_init = set_commands

    logger.info('running bot')
    application.run_polling()

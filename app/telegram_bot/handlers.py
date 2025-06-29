from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, ContextTypes, filters, ConversationHandler, MessageHandler

from app.telegram_bot.keyboards import markup_filters, markup_front, markup_backend, markup_settings
#from app.telegram_bot.utils import save_to_db
from app.telegram_bot.fsm import create_settings_handler


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Привет {update.effective_user.username}, введите /subscribe')

async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    #await save_to_db(update.effective_user.username)
    await update.message.reply_text('Вы подписаны на рассылку, введете /settings для настройки фильтра')

async def subscribe_to_vacancies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Вы подписаны на рассылку вакансий, введете /settings для настройки фильтра')

async def my_subscribes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Вот список ваших подписок')

async def loads(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Вот выгрузка списка вакансий в выбранном вами формате')


#==============================Handlers Setup==============================

def setup_handlers(application: Application):
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('subscribe', subscribe))
    application.add_handler(CommandHandler('subscribe_to_vacancies', subscribe_to_vacancies))
    application.add_handler(CommandHandler('my_subscribes', my_subscribes))
    application.add_handler(CommandHandler('loads', loads))
    
    # Добавляем ConversationHandler первым, чтобы он перехватывал команду /settings
    application.add_handler(create_settings_handler)
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from asgiref.sync import sync_to_async
from telegram.ext import Application, CommandHandler, ContextTypes, filters, ConversationHandler, MessageHandler

from app.telegram_bot.models import TgUser, UserSubscriptionSettings
from app.telegram_bot.state_machine import settings, settings_handler
from app.telegram_bot.utils import get_or_create_user

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f'Привет {update.effective_user.username}, введите /subscribe чтобы подписаться на рассылку вакансий')

async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.effective_user.username
    user_id = update.effective_user.id
    user = await get_or_create_user(username=username, user_id=user_id, is_subscribed=True)
    await update.message.reply_text('Вы подписаны на рассылку вакансий, введете /settings для настройки фильтра')




def setup_handlers(application: Application):
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('subscribe', subscribe))
    application.add_handler(settings_handler)



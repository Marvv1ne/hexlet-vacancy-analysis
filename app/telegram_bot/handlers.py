from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from asgiref.sync import sync_to_async
from telegram.ext import Application, CommandHandler, ContextTypes, filters, ConversationHandler, MessageHandler

from app.telegram_bot.models import TgUser, UserSubscriptionSettings
from app.telegram_bot.statate_machine import settings, settings_handler

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f'Привет {update.effective_user.username}, введите /subscribe чтобы подписаться на рассылку вакансий')

async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.effective_user.username
    chat_id = update.effective_user.id
    user = await sync_to_async(TgUser.objects.get_or_create, thread_sensitive=True)(
    username=username, chat_id=chat_id, is_subscribed=True
)
    await update.message.reply_text('Вы подписаны на рассылку вакансий, введете /settings для настройки фильтра')




def setup_handlers(application: Application):
    application.add_handler(CommandHandler('start', start))
    #application.add_handler(CommandHandler('settings', settings))
    application.add_handler(CommandHandler('subscribe', subscribe))
    application.add_handler(settings_handler)



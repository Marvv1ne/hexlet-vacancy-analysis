import logging

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from app.settings import TELEGRAM_BOT_TOKEN

logger = logging.getLogger('django')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Hello {update.effective_user.username}')


def run_bot():
    '''Main function for start telegram bot'''
    logger.info('starting managment command')
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler (CommandHandler('start', start))

    logger.info('running bot')
    application.run_polling()

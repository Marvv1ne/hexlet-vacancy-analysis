import logging
import asyncio
from os import name

from asgiref.sync import sync_to_async
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, BotCommand, Bot
from telegram.ext import Application, CommandHandler, ContextTypes, filters, ConversationHandler, MessageHandler

from app.settings import TELEGRAM_BOT_TOKEN
from .models import TgUser

logger = logging.getLogger('django')

keyboard_prof = [
    ['frontend', 'backend'],
    ['Done'],
]

keyboard_front = [
    ['Angular', 'React', 'JS'],
    ['HTML', 'CSS', 'Vue.js'],
    ['Done'],
]

keyboard_backend = [
    ['Java', 'Nodejs', 'Go'],
    ['Python', 'PHP', 'C++'],
    ['Done'],
]

markup_prof = ReplyKeyboardMarkup(keyboard_prof, one_time_keyboard=True)
markup_front = ReplyKeyboardMarkup(keyboard_front)
markup_backend = ReplyKeyboardMarkup(keyboard_backend)

CHOOSE_PROF, CHOOSE_BACK, CHOOSE_FRONT = range(3)

@sync_to_async
def save_to_db(username=name, filters=None):
    TgUser.objects.update_or_create(username=username, filters='some_filter')
    

async def set_commands(application: Application) -> None:
    await application.bot.set_my_commands([('start', 'start the bot'),
                                         ('subscribe', 'subscribe to sending you vacancies'),
                                         ('settings', 'setting up filter for vacancies'),
                                         ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Привет {update.effective_user.username}, введите /subscribe')

async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await save_to_db(update.effective_user.username)
    await update.message.reply_text('Вы подписаны на рассылку, введете /settings для настройки фильтра')

# FSM

async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    markup_key = ReplyKeyboardMarkup(keyboard_prof, one_time_keyboard=True)
    await update.message.reply_text('Choose profession', reply_markup=markup_key)
    return CHOOSE_PROF

async def set_frontend(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_data = context.user_data
    text = update.message.text
    print(text)
    if 'frontend' not in user_data:
        context.user_data['frontend'] = [text]
    else:
        context.user_data['frontend'].append(text)
    markup_key = ReplyKeyboardMarkup(keyboard_front)
    await update.message.reply_text('Choose stack', reply_markup=markup_key)
    return CHOOSE_FRONT

async def set_backend(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_data = context.user_data
    text = update.message.text
    print(text)
    if 'backend' not in user_data:
        user_data['backend'] = [text]
    else:
        user_data['backend'].append(text)
    markup_key = ReplyKeyboardMarkup(keyboard_backend)
    await update.message.reply_text('Choose stack', reply_markup=markup_key)
    return CHOOSE_BACK

async def recived_information(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    pass

async def done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_data = context.user_data
    await update.message.reply_text(f'Это твои настройки {user_data}', reply_markup=ReplyKeyboardRemove())
    await save_to_db(username=update.effective_user.username, filters=user_data)
    user_data.clear()
    return ConversationHandler.END

conv_handler = ConversationHandler(
    entry_points=[CommandHandler('settings', settings)],
    states={
        CHOOSE_PROF: [
            MessageHandler(filters.Regex("^(frontend)$"), set_frontend),
            MessageHandler(filters.Regex("^(backend)$"), set_backend),
        ],
        CHOOSE_FRONT: [
            MessageHandler(filters.Regex("^(Angular|Vue.js|JS|HTML|CSS|React)$"), set_frontend),
        ],
        CHOOSE_BACK: [
            MessageHandler(filters.Regex("^(Python|Java|Nodejs|Go|PHP|C++)$"), set_backend),
        ],
    },
    fallbacks=[MessageHandler(filters.Regex("^Done$"), done)],
)


# Commands



async def set_commands(application: Application) -> None:
    await application.bot.set_my_commands([('start', 'start the bot'),
                                         ('subscribe', 'subscribe to sending you vacancies'),
                                         ('settings', 'setting up filter for vacancies'),
                                         ])

def run_bot():
    '''Main function for start telegram bot'''
    logger.info('starting managment command')
    
    
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('subscribe', subscribe))
    application.add_handler(conv_handler)

    logger.info('running bot')
    application.run_polling()

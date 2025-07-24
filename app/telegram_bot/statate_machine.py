from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, CommandHandler, filters
from asgiref.sync import sync_to_async
from django_celery_beat.models import PeriodicTask

from app.telegram_bot.keyboards import (
    markup_filters, markup_front, markup_backend,
    markup_settings, markup_interval
)

from app.telegram_bot.models import TgUser, UserSubscriptionSettings
from app.telegram_bot.utils import save_subscription_settings_to_db

CHOOSE_SETTINGS, CHOOSE_FILTERS, CHOOSE_FRONT, CHOOSE_BACK, CHOOSE_INTERVAL, CHOOSE_FRONT_MULTI, CHOOSE_BACK_MULTI, CONFIRM_DELETE = range(8)

#============================Show=settings============================

async def show_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.effective_user.username

    user = await sync_to_async(TgUser.objects.get, thread_sensitive=True)(username=username)
    settings = await sync_to_async(UserSubscriptionSettings.objects.get(user=user), thread_sensitive=True)()
    if settings:
        filter = ', '.join(list(settings.filters))
        await update.message.reply_text(filter)
    else:
        await update.message.reply_text('У вас еще нет натроенного фильтра вакансий')

#==========================Create=or=Update=Stage======================

async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    username = update.effective_user.username
    context.user_data['step'] = 'settings'
    user, created = await sync_to_async(TgUser.objects.get_or_create, thread_sensitive=True)(username=username)
    if user.is_subscribed:
        await update.message.reply_text("Тут вы можете настроить свои фильтры", reply_markup=markup_settings)
        return CHOOSE_SETTINGS
    await update.message.reply_text("Вы должны подписаться на рассылку")

async def create_or_update_settings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['step'] = 'create_or_update'
    await update.message.reply_text("Выберите профессию (frontend/backend):", reply_markup=markup_filters)
    return CHOOSE_FILTERS

#==========================Show=Settings=========================

async def show_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.effective_user.username
    user = await sync_to_async(TgUser.objects.get, thread_sensitive=True)(username=username)
    settings = await sync_to_async(UserSubscriptionSettings.objects.get, thread_sensitive=True)(user=user.id)
    if settings:
        filter = ', '.join(list(settings.filters))
        await update.message.reply_text(f'Ваши настройки фильтра: {filter}')
    else:
        await update.message.reply_text('У вас еще нет натроенного фильтра вакансий')

#==========================Delete=Stage======================

async def delete_settings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    username = update.effective_user.username
    user = await sync_to_async(TgUser.objects.get, thread_sensitive=True)(username=username)
    subscription = await sync_to_async(UserSubscriptionSettings.objects.get, thread_sensitive=True)(user=user.id)
    if subscription:
        context.user_data['subscription_id'] = subscription.id
        await update.message.reply_text(
                "Вы уверены, что хотите удалить все настройки фильтра? (Да/Нет)",
                reply_markup=ReplyKeyboardRemove()
            )
        return CONFIRM_DELETE
    await update.message.reply_text("Нет сохранённых настроек для удаления.", reply_markup=markup_settings)
    return CHOOSE_SETTINGS

async def confirm_delete(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    answer = update.message.text.strip().lower()
    username = update.effective_user.username
    user = await sync_to_async(TgUser.objects.get, thread_sensitive=True)(username=username)
    subscription = await sync_to_async(UserSubscriptionSettings.objects.get, thread_sensitive=True)(user=user.id)
    if answer == 'да':
        subscription_id = context.user_data.get('delete_subscription_id')
        settings = await sync_to_async(UserSubscriptionSettings.objects.get, thread_sensitive=True)(id=subscription.id)
        task = await sync_to_async(PeriodicTask.objects.get, thread_sensitive=True)(name=f"user_{user.id}_subscription_{subscription.id}")
        await sync_to_async(settings.delete)()
        await sync_to_async(task.delete)()
        await update.message.reply_text("Ваши настройки и рассылка удалены.", reply_markup=markup_settings)
        return CHOOSE_SETTINGS
    else:
        await update.message.reply_text("Удаление отменено.", reply_markup=markup_settings)
        return CHOOSE_SETTINGS

#==========================Filters=Stage======================

async def select_profession(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    profession = update.message.text
    context.user_data['step'] = 'profession'
    context.user_data.setdefault('profession', set()).add(profession)
    match profession:
        case 'frontend':
            context.user_data['step'] = 'frontend'
            await update.message.reply_text("Выберите стек фронтенда (можно выбрать несколько):", reply_markup=markup_front)
            return CHOOSE_FRONT_MULTI
        case 'backend':
            context.user_data['step'] = 'backend'
            await update.message.reply_text("Выберите стек бэкенда (можно выбрать несколько):", reply_markup=markup_backend)
            return CHOOSE_BACK_MULTI
        case _:
            await update.message.reply_text("что то пошло не так", reply_markup=markup_filters)

#====================================Frontend=Stage================================

async def select_frontend_stack(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    stack = update.message.text
    context.user_data['step'] = 'frontend'
    context.user_data.setdefault('frontend_stack', set()).add(stack)
    current_stack = ", ".join(context.user_data["frontend_stack"])
    await update.message.reply_text(
        f"Выбранные технологии: {current_stack}\n"
        f"Выберите еще технологии или нажмите 'Готово':",
        reply_markup=markup_front
    )
    return CHOOSE_FRONT_MULTI

#====================================Backend=Stage============================

async def select_backend_stack(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    stack = update.message.text
    context.user_data['step'] = 'backend'
    context.user_data.setdefault('backend_stack', set()).add(stack)
    current_stack = ", ".join(context.user_data["backend_stack"])
    await update.message.reply_text(
        f"Выбранные технологии: {current_stack}\n"
        f"Выберите еще технологии или нажмите 'Готово':",
        reply_markup=markup_backend
    )
    return CHOOSE_BACK_MULTI


#====================================Iterval=Stage============================

async def set_interval(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    interval = update.message.text
    
    context.user_data["interval"] = interval
    return await done(update, context)

#==============================Cancel=Finish=Selection=Stage=========================

async def finish_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    #context.user_data["step"] = "interval" # Под вопросом
    stack_name = context.user_data['step'] + '_stack'
    stack = context.user_data.get(stack_name, set())
    context.user_data.setdefault("filters", set()).update(stack)
    context.user_data["step"] = "interval"
    await update.message.reply_text("Выберите интервал получения уведомлений:", reply_markup=markup_interval)
    return CHOOSE_INTERVAL

async def cancel_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    
    context.user_data.clear()
    await update.message.reply_text(
        "Вы сбросили настройки.",
        reply_markup=markup_settings
    )
    return CHOOSE_SETTINGS

#===============================Done=And=Back=====================================

async def back_to_previose_stage(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    step = context.user_data.get('step')
    match step:
        case "create_or_update":
            await update.message.reply_text("Назад настройкам:", reply_markup=markup_settings)
            return CHOOSE_SETTINGS
        case 'profession':
            context.user_data["step"] = "create_or_update"
            await update.message.reply_text("Назад настройкам:", reply_markup=markup_settings)
            return CHOOSE_SETTINGS
        case 'frontend':
            context.user_data["step"] = "profession"
            await update.message.reply_text("Назад к выбору профессии:", reply_markup=markup_filters)
            return CHOOSE_FILTERS
        case 'backend':
            context.user_data["step"] = "profession"
            await update.message.reply_text("Назад к выбору профессии:", reply_markup=markup_filters)
            return CHOOSE_FILTERS
        case 'interval':
            if 'backend_stack' in context.user_data:
                context.user_data["step"] = "backend"
                await update.message.reply_text("Назад к выбору бэкенд стека:", reply_markup=markup_backend)
                return CHOOSE_BACK_MULTI
            elif 'frontend_stack' in context.user_data:
                context.user_data["step"] = "frontend"
                await update.message.reply_text("Назад к выбору фронтенд стека:", reply_markup=markup_front)
                return CHOOSE_FRONT_MULTI
            else:
                #Для отладки
                await update.message.reply_text(f"Что то пошло не так\n{context.user_data.profession}", reply_markup=ReplyKeyboardRemove())


async def done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_data = context.user_data
    username = update.effective_user.username
    chat_id = update.effective_user.id

    filters = list(user_data.get("filters", []))
    interval = user_data.get("interval", "не задан")

    await update.message.reply_text(
        f"Ваши настройки сохранены:\n"
        f"Фильтры: {', '.join(filters)}\n"
        f"Интервал: {interval}\n",
        reply_markup=ReplyKeyboardRemove()
    )

    await save_subscription_settings_to_db(username, filters, interval)
    user_data.clear()
    return ConversationHandler.END

async def exit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Выход из настроек фильтра", reply_markup=ReplyKeyboardRemove())
    context.user_data.clear()
    return ConversationHandler.END

settings_handler = ConversationHandler(
    entry_points=[
        CommandHandler('settings', settings),
    ],
    states={
        CHOOSE_SETTINGS: [
            MessageHandler(filters.Regex("^create_or_update_settings$"), create_or_update_settings),
            MessageHandler(filters.Regex("^show_settings$"), show_settings),
            MessageHandler(filters.Regex("^delete_settings$"), delete_settings),
            MessageHandler(filters.Regex("^Done$"), done),
        ],

        CHOOSE_FILTERS: [
            MessageHandler(filters.Regex("^(frontend|backend)$"), select_profession),
        ],

        CHOOSE_FRONT_MULTI: [
            MessageHandler(filters.Regex("^(Angular|Vue\\.js|JS|HTML|CSS|React)$"), select_frontend_stack),
            MessageHandler(filters.Regex("^Готово$"), finish_selection),
            MessageHandler(filters.Regex("^Отменить выбор$"), cancel_selection),
        ],

        CHOOSE_BACK_MULTI: [
            MessageHandler(filters.Regex("^(Python|Java|Nodejs|Go|PHP|C\\+\\+)$"), select_backend_stack),
            MessageHandler(filters.Regex("^Готово$"), finish_selection),
            MessageHandler(filters.Regex("^Отменить выбор$"), cancel_selection),
        ],

        CHOOSE_INTERVAL: [
            MessageHandler(filters.Regex("^(minute|day|week)$"), set_interval),
             MessageHandler(filters.Regex("^Отменить выбор$"), cancel_selection),
        ],

        CONFIRM_DELETE: [
            MessageHandler(filters.TEXT & (~filters.COMMAND), confirm_delete),
        ],
    },

     fallbacks=[
        MessageHandler(filters.Regex("^exit$"), exit),
        MessageHandler(filters.Regex("^Done$"), done),
        MessageHandler(filters.Regex("^🔙 Назад$"), back_to_previose_stage),
    ],
)




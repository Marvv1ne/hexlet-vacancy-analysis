from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, CommandHandler, filters
from asgiref.sync import sync_to_async
from django_celery_beat.models import PeriodicTask

from app.telegram_bot.keyboards import (
    markup_filters, markup_front, markup_backend,
    markup_settings, markup_format, markup_interval
)
from app.telegram_bot.models import TgUser, UserSubscription
# from app.telegram_bot.utils import save_to_db

# Добавляем новые состояния для множественного выбора
CHOOSE_SETTINGS, CHOOSE_FILTERS, CHOOSE_FRONT, CHOOSE_BACK, CHOOSE_INTERVAL, CHOOSE_FORMAT, CHOOSE_FRONT_MULTI, CHOOSE_BACK_MULTI, CONFIRM_DELETE = range(9)

# ======================= Start Settings Flow =======================

async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Выберите действие:", reply_markup=markup_settings)
    return CHOOSE_SETTINGS

async def create_settings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Выберите направление (frontend/backend):", reply_markup=markup_filters)
    return CHOOSE_FILTERS

async def update_settings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    username = update.effective_user.username
    user = await sync_to_async(TgUser.objects.filter(username=username).first)()
    if user:
        subscription = await sync_to_async(UserSubscription.objects.filter(user=user, is_active=True).first)()
        if subscription:
            context.user_data["filters"] = set(subscription.filters.get("filters", []))
            context.user_data["interval"] = subscription.interval
            context.user_data["format"] = subscription.format
            await update.message.reply_text(
                f"Редактирование настроек:\n"
                f"Текущие фильтры: {', '.join(context.user_data['filters'])}\n"
                f"Текущий интервал: {context.user_data['interval']}\n"
                f"Текущий формат: {context.user_data['format']}\n"
                "Выберите направление (frontend/backend) для изменения фильтров:",
                reply_markup=markup_filters
            )
            return CHOOSE_FILTERS
    await update.message.reply_text("Нет сохранённых настроек. Сначала создайте их.")
    return CHOOSE_SETTINGS

async def delete_settings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    username = update.effective_user.username
    user = await sync_to_async(TgUser.objects.filter(username=username).first)()
    if user:
        subscription = await sync_to_async(UserSubscription.objects.filter(user=user, is_active=True).first)()
        if subscription:
            context.user_data['delete_subscription_id'] = subscription.id
            await update.message.reply_text(
                "Вы уверены, что хотите удалить все настройки и рассылку? (Да/Нет)",
                reply_markup=ReplyKeyboardRemove()
            )
            return CONFIRM_DELETE
    await update.message.reply_text("Нет сохранённых настроек для удаления.", reply_markup=markup_settings)
    return CHOOSE_SETTINGS

async def confirm_delete(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    answer = update.message.text.strip().lower()
    if answer in ["да", "yes", "y"]:
        username = update.effective_user.username
        user = await sync_to_async(TgUser.objects.filter(username=username).first)()
        if user:
            sub_id = context.user_data.get('delete_subscription_id')
            subscription = await sync_to_async(UserSubscription.objects.filter(id=sub_id, user=user).first)()
            if subscription:
                # Удаляем связанные задачи celery-beat
                await sync_to_async(PeriodicTask.objects.filter(
                    name=f"user_{user.id}_subscription_{subscription.id}"
                ).delete)()
                await sync_to_async(subscription.delete)()
                await update.message.reply_text("Ваши настройки и рассылка удалены.", reply_markup=markup_settings)
                return CHOOSE_SETTINGS
        await update.message.reply_text("Ошибка при удалении настроек.", reply_markup=markup_settings)
        return CHOOSE_SETTINGS
    else:
        await update.message.reply_text("Удаление отменено.", reply_markup=markup_settings)
        return CHOOSE_SETTINGS

# ======================= Filter Selection =======================

async def set_filters(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    profession = update.message.text
    context.user_data["step"] = "filters"
    context.user_data.setdefault("filters", set()).add(profession)

    if profession.lower() == "frontend":
        await update.message.reply_text("Выберите стек фронтенда (можно выбрать несколько):", reply_markup=markup_front)
        return CHOOSE_FRONT_MULTI
    elif profession.lower() == "backend":
        await update.message.reply_text("Выберите стек бэкенда (можно выбрать несколько):", reply_markup=markup_backend)
        return CHOOSE_BACK_MULTI
    else:
        await update.message.reply_text("Неверный выбор. Пожалуйста, выберите frontend или backend.")
        return CHOOSE_FILTERS

# ======================= Multiple Choice Frontend =======================

async def set_frontend_multi(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    stack = update.message.text
    context.user_data["step"] = "front_multi"
    
    # Инициализируем множественный выбор
    if "frontend_stack" not in context.user_data:
        context.user_data["frontend_stack"] = set()
    
    # Добавляем выбранную технологию
    context.user_data["frontend_stack"].add(stack)
    
    # Показываем текущий выбор
    current_stack = ", ".join(context.user_data["frontend_stack"])
    await update.message.reply_text(
        f"Выбранные технологии: {current_stack}\n"
        f"Выберите еще технологии или нажмите 'Готово':",
        reply_markup=markup_front
    )
    return CHOOSE_FRONT_MULTI

async def cancel_frontend_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Отменяет выбор фронтенд технологий"""
    if "frontend_stack" in context.user_data:
        context.user_data["frontend_stack"].clear()
    
    await update.message.reply_text(
        "Выбор отменен. Выберите технологии заново:",
        reply_markup=markup_front
    )
    return CHOOSE_FRONT_MULTI

async def finish_frontend_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # Добавляем все выбранные фронтенд технологии в общие фильтры
    frontend_stack = context.user_data.get("frontend_stack", set())
    context.user_data.setdefault("filters", set()).update(frontend_stack)
    
    await update.message.reply_text("Выберите интервал получения уведомлений:", reply_markup=markup_interval)
    return CHOOSE_INTERVAL

# ======================= Multiple Choice Backend =======================

async def set_backend_multi(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    stack = update.message.text
    context.user_data["step"] = "back_multi"
    
    # Инициализируем множественный выбор
    if "backend_stack" not in context.user_data:
        context.user_data["backend_stack"] = set()
    
    # Добавляем выбранную технологию
    context.user_data["backend_stack"].add(stack)
    
    # Показываем текущий выбор
    current_stack = ", ".join(context.user_data["backend_stack"])
    await update.message.reply_text(
        f"Выбранные технологии: {current_stack}\n"
        f"Выберите еще технологии или нажмите 'Готово':",
        reply_markup=markup_backend
    )
    return CHOOSE_BACK_MULTI

async def cancel_backend_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Отменяет выбор бэкенд технологий"""
    if "backend_stack" in context.user_data:
        context.user_data["backend_stack"].clear()
    
    await update.message.reply_text(
        "Выбор отменен. Выберите технологии заново:",
        reply_markup=markup_backend
    )
    return CHOOSE_BACK_MULTI

async def finish_backend_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # Добавляем все выбранные бэкенд технологии в общие фильтры
    backend_stack = context.user_data.get("backend_stack", set())
    context.user_data.setdefault("filters", set()).update(backend_stack)
    
    await update.message.reply_text("Выберите интервал получения уведомлений:", reply_markup=markup_interval)
    return CHOOSE_INTERVAL

# ======================= Interval & Format =======================

async def set_interval(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    interval = update.message.text
    context.user_data["step"] = "interval"
    context.user_data["interval"] = interval
    await update.message.reply_text("Выберите формат загрузки:", reply_markup=markup_format)
    return CHOOSE_FORMAT

async def set_format(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    load_format = update.message.text
    context.user_data["step"] = "format" 
    context.user_data["format"] = load_format

    return await done(update, context)

# ======================= Done and go_back =======================

async def go_back(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    step = context.user_data.get("step")

    if step == "filters":
        await update.message.reply_text("Назад к выбору направления:", reply_markup=markup_filters)
        return CHOOSE_FILTERS
    elif step == "front_multi":
        await update.message.reply_text("Назад к выбору фронтенд стека:", reply_markup=markup_front)
        return CHOOSE_FRONT_MULTI
    elif step == "back_multi":
        await update.message.reply_text("Назад к выбору бэкенд стека:", reply_markup=markup_backend)
        return CHOOSE_BACK_MULTI
    elif step == "interval":
        await update.message.reply_text("Назад к выбору интервала:", reply_markup=markup_interval)
        return CHOOSE_INTERVAL
    elif step == "format":
        await update.message.reply_text("Назад к выбору формата:", reply_markup=markup_format)
        return CHOOSE_FORMAT
    else:
        await update.message.reply_text("Вы вернулись в главное меню настроек.", reply_markup=markup_settings)
        return CHOOSE_SETTINGS


async def done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_data = context.user_data
    filters = list(user_data.get("filters", []))
    interval = user_data.get("interval", "не задан")
    load_format = user_data.get("format", "не задан")
    username = update.effective_user.username
    chat_id = update.effective_user.id
    # email можно запросить у пользователя отдельным шагом, если нужно

    await update.message.reply_text(
        f"Ваши настройки сохранены:\n"
        f"Фильтры: {', '.join(filters)}\n"
        f"Интервал: {interval}\n"
        f"Формат: {load_format}",
        reply_markup=ReplyKeyboardRemove()
    )

    # Сохраняем пользователя и подписку
    await save_user_and_subscription(username, chat_id, filters, interval, load_format)

    user_data.clear()
    return ConversationHandler.END


@sync_to_async
def save_user_and_subscription(username, chat_id, filters, interval, load_format):
    user, _ = TgUser.objects.get_or_create(username=username, defaults={"chat_id": chat_id})
    user.chat_id = chat_id
    user.save()
    # Пытаемся найти активную подписку
    subscription = UserSubscription.objects.filter(user=user, is_active=True).first()
    if subscription:
        subscription.filters = {"filters": filters}
        subscription.interval = interval
        subscription.format = load_format
        subscription.save()
    else:
        UserSubscription.objects.create(
            user=user,
            filters={"filters": filters},
            interval=interval,
            format=load_format,
            send_via_email=False,
            send_via_telegram=True,
            is_active=True,
        )

# ======================= Conversation Handler =======================

create_settings_handler = ConversationHandler(
    entry_points=[
        CommandHandler('settings', settings),
        MessageHandler(filters.Regex("^Настройки$"), settings)
    ],
    states={
        CHOOSE_SETTINGS: [
            MessageHandler(filters.Regex("^create_settings$"), create_settings),
            MessageHandler(filters.Regex("^update_settings$"), update_settings),
            MessageHandler(filters.Regex("^delete_settings$"), delete_settings),
            MessageHandler(filters.Regex("^Done$"), done),
        ],
        CHOOSE_FILTERS: [
            MessageHandler(filters.Regex("^(frontend|backend)$"), set_filters),
        ],
        CHOOSE_FRONT_MULTI: [
            MessageHandler(filters.Regex("^(Angular|Vue\\.js|JS|HTML|CSS|React)$"), set_frontend_multi),
            MessageHandler(filters.Regex("^Готово$"), finish_frontend_selection),
            MessageHandler(filters.Regex("^Отменить выбор$"), cancel_frontend_selection),
        ],
        CHOOSE_BACK_MULTI: [
            MessageHandler(filters.Regex("^(Python|Java|Nodejs|Go|PHP|C\\+\\+)$"), set_backend_multi),
            MessageHandler(filters.Regex("^Готово$"), finish_backend_selection),
            MessageHandler(filters.Regex("^Отменить выбор$"), cancel_backend_selection),
        ],
        CHOOSE_INTERVAL: [
            MessageHandler(filters.Regex("^(minute|day|week)$"), set_interval),
        ],
        CHOOSE_FORMAT: [
            MessageHandler(filters.Regex("^(PDF|Excel)$"), set_format),
        ],
        CONFIRM_DELETE: [
            MessageHandler(filters.TEXT & (~filters.COMMAND), confirm_delete),
        ],
    },
    fallbacks=[
        MessageHandler(filters.Regex("^Done$"), done),
        MessageHandler(filters.Regex("^🔙 Назад$"), go_back),
    ]
)

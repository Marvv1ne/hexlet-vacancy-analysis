import logging
from typing import Dict
from app.telegram_bot.models import TgUser, UserSubscriptionSettings
from django_celery_beat.models import CrontabSchedule
from asgiref.sync import sync_to_async
from app.telegram_bot.models import TgUser, UserSubscriptionSettings

@sync_to_async
def get_or_create_user(username):
    user = TgUser.objects.get_or_create(username=username)
    return user

@sync_to_async
def get_user_subscription(user_id):
    try:
        subscription = UserSubscriptionSettings.objects.get(user=user_id)
        return subscription
    except UserSubscriptionSettings.DoesNotExist:
        return None

    


@sync_to_async
def save_subscription_settings_to_db(username, filters, interval_choice):
    """
    Сохраняет или обновляет настройки подписки пользователя с нужным crontab-расписанием.
    выбор интервала: 'minute', 'day', 'week'
    """
    user = TgUser.objects.get(username=username)
    if interval_choice == 'minute':
        crontab, _ = CrontabSchedule.objects.get_or_create(
            minute='*', hour='*', day_of_week='*', day_of_month='*', month_of_year='*'
        )
    elif interval_choice == 'day':
        crontab, _ = CrontabSchedule.objects.get_or_create(
            minute='0', hour='9', day_of_week='*', day_of_month='*', month_of_year='*'
        )
    elif interval_choice == 'week':
        crontab, _ = CrontabSchedule.objects.get_or_create(
            minute='0', hour='10', day_of_week='1', day_of_month='*', month_of_year='*'
        )
    else:
        raise ValueError('Unknown interval')

    subscription, _ = UserSubscriptionSettings.objects.update_or_create(
        user=user,
        filters= filters,
        crontab= crontab,
    )




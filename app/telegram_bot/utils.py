import logging
from app.telegram_bot.models import TgUser, UserSubscriptionSettings
from django_celery_beat.models import CrontabSchedule
from asgiref.sync import sync_to_async

@sync_to_async
def save_subscription_settings_to_db(username, filters, interval_choice):
    """
    Сохраняет или обновляет настройки подписки пользователя с нужным crontab-расписанием.
    interval_choice: 'minute', 'day', 'week'
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

    subscription, _ = UserSubscriptionSettings.objects.get_or_create(
        user=user,
        filters= filters,
        crontab= crontab,
    )




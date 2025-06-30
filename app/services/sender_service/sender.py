import os
from django.core.mail import send_mail
from django.conf import settings
from telegram import Bot
from celery import shared_task


def send_email_message(to_email, subject, message):
    """
    Отправить email через стандартный Django backend.
    Требует настройки EMAIL_HOST и других параметров в settings.py.
    """
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [to_email],
        fail_silently=False,
    )


def send_telegram_message(chat_id, message):
    """
    Отправить сообщение через Telegram-бота.
    Требует TELEGRAM_BOT_TOKEN в settings.py или переменных окружения.
    """
    token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None) or os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        raise ValueError('TELEGRAM_BOT_TOKEN не задан в настройках!')
    bot = Bot(token=token)
    bot.send_message(chat_id=chat_id, text=message)

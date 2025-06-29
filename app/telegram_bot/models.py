from operator import mod
from django.db import models
from django.contrib.postgres.fields import JSONField
from django_celery_beat.models import PeriodicTask, IntervalSchedule
from django.db.models.signals import post_save
from django.dispatch import receiver
import json

# Create your models here.
class TgUser(models.Model):
    username = models.CharField(max_length=50)
    chat_id = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now=True)

class UserSubscription(models.Model):
    user = models.ForeignKey(TgUser, on_delete=models.CASCADE, related_name='subscriptions')
    filters = models.JSONField(default=dict)  # Сохраняем фильтры как JSON
    interval = models.CharField(max_length=20)  # 'minutes', 'hours', 'days', 'weeks'
    format = models.CharField(max_length=20)
    send_via_email = models.BooleanField(default=False)
    send_via_telegram = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


def create_or_update_periodic_task(subscription):
    # Преобразуем user interval в совместимый с IntervalSchedule
    period_map = {
        'minute': 'minutes',
        'day': 'days',
        'week': 'weeks',
        'hour': 'hours',
        'seconds': 'seconds',
    }
    period = period_map.get(subscription.interval, 'days')
    interval, _ = IntervalSchedule.objects.get_or_create(
        every=1,
        period=period
    )

    # Формируем параметры задачи
    if subscription.send_via_telegram and subscription.user.chat_id:
        task_name = 'app.services.sender_service.sender.send_telegram_message_task'
        args = json.dumps([subscription.user.chat_id, f"Ваша рассылка: {subscription.filters}"])
    elif subscription.send_via_email and subscription.user.email:
        task_name = 'app.services.sender_service.sender.send_email_message_task'
        args = json.dumps([subscription.user.email, "Ваша рассылка", str(subscription.filters)])
    else:
        return

    PeriodicTask.objects.update_or_create(
        name=f"user_{subscription.user.id}_subscription_{subscription.id}",
        defaults={
            'interval': interval,
            'task': task_name,
            'args': args,
            'enabled': subscription.is_active,
        }
    )


@receiver(post_save, sender=UserSubscription)
def create_periodic_task_for_subscription(sender, instance, created, **kwargs):
    create_or_update_periodic_task(instance)
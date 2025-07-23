import json
import logging

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.postgres.fields import JSONField # Зачем этот импорт????
from django_celery_beat.models import PeriodicTask, IntervalSchedule
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_celery_beat.models import CrontabSchedule

class TgUser(models.Model):
    username = models.CharField(max_length=50, unique=True)
    chat_id=models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    is_subscribed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now=True)

class UserSubscriptionSettings(models.Model):
    user = models.ForeignKey(TgUser, on_delete=models.CASCADE, related_name=_('Пользователь'))    
    filters = models.JSONField(default=dict, verbose_name=_('Настройки фильтра'))
    crontab = models.ForeignKey(
        CrontabSchedule,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subscriptions'
    )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.crontab:
            PeriodicTask.objects.update_or_create(
                name=f"user_{self.user.id}_subscription_{self.id}",
                defaults={
                    'crontab': self.crontab,
                    'task': 'app.services.sender_service.tasks.send_telegram_message_task',
                    'args': json.dumps([self.user.chat_id, self.filters]),
                    'enabled': self.user.is_subscribed,
                }
            )

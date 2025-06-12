from operator import mod
from django.db import models

# Create your models here.
class TgUser(models.Model):
    username = models.CharField(max_length=50)
    filters = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now=True)
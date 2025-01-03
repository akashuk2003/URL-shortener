# shortener/models.py
from django.db import models
import string
import random
from django.conf import settings


class URL(models.Model):
    original_url = models.URLField(max_length=2000)
    short_code = models.CharField(max_length=10, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    clicks = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.original_url} -> {self.short_code}"

    @classmethod
    def create_short_code(cls):
        characters = string.ascii_letters + string.digits
        short_code = ''.join(random.choices(characters, k=6))

        while cls.objects.filter(short_code=short_code).exists():
            short_code = ''.join(random.choices(characters, k=6))

        return short_code

    def get_absolute_url(self):
        return f"{settings.SITE_URL}/{self.short_code}"
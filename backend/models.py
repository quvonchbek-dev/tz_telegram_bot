from django.db import models


class BotUser(models.Model):
    class Lang(models.TextChoices):
        UZ = 'uz'
        RU = 'ru'
        EN = 'en'

    class Status(models.IntegerChoices):
        ACTIVE = 1
        BLOCKED = 2

    chat_id = models.CharField(unique=True, max_length=255)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    username = models.CharField(max_length=255, null=True, blank=True)

    status = models.IntegerField(choices=Status.choices, default=Status.ACTIVE)
    lang = models.CharField(max_length=2, choices=Lang.choices, default=Lang.UZ)
    joined = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(auto_now=True)

    def get_full_name(self):
        return ' '.join([self.first_name, self.last_name or ''])

    def __str__(self):
        return self.get_full_name()


class BotAdmin(models.Model):
    admin = models.ForeignKey(BotUser, on_delete=models.CASCADE, unique=True)
    admins = models.Manager()

    def __str__(self):
        return self.admin.get_full_name()


class Channel(models.Model):
    title = models.CharField(max_length=255)
    chat_id = models.CharField(unique=True, max_length=255, default="-")
    invite_link = models.URLField(unique=True)

    def __str__(self) -> str:
        return self.title

import os.path
from enum import auto

from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator
from pyrogram.enums import ParseMode

User = get_user_model()


def get_upload_path(instance, filename):
    return os.path.join(
        f'{instance.user_id}',
        # f'{instance.account_id}',
        filename
    )


class AccountType(models.TextChoices):
    TIK_TOK = 'TikTok'
    INSTAGRAM = 'Instagram'
    # FACEBOOK = 'Facebook'
    TELEGRAM = 'Telegram'
    # VK = 'Vk'


class Account(models.Model):
    type = models.CharField(max_length=20, choices=AccountType.choices, blank=False)
    token = models.TextField(blank=False, null=False)

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        unique_together = ['type', 'user']

    def __str__(self):
        return self.type


class Post(models.Model):
    # message_id = models.IntegerField(unique=True, null=False, blank=False)
    # ParseModeChoices = (
    #     (ParseMode.DEFAULT, "DEFAULT"),
    #     (ParseMode.MARKDOWN, "MARKDOWN"),
    #     (ParseMode.HTML, "HTML"),
    #     (ParseMode.DISABLED, "DISABLED"),
    # )
    class ParseModeChoices(models.TextChoices):
        DEFAULT = "DEFAULT"
        MARKDOWN = "MARKDOWN"
        HTML = "HTML"
        DISABLED = "DISABLED"

    title = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    hash_tag = models.TextField(blank=True)
    photo = models.ImageField(upload_to=get_upload_path, blank=True, null=True)
    video = models.FileField(
        upload_to=get_upload_path,
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['mp4', 'mov'])]
    )
    parse_mode = models.CharField(
        max_length=20,
        choices=ParseModeChoices.choices,
        blank=True,
        default=None
    )

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    accounts = models.ManyToManyField(Account)
    chats = models.ManyToManyField("Chat")
    message_ids = models.ManyToManyField("Message")

    def __str__(self):
        return self.title


class Chat(models.Model):
    chat_id = models.TextField(blank=False)
    account_type = models.CharField(max_length=20, choices=AccountType.choices, blank=False)

    # post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f'{self.chat_id} : {self.account_type}'


class Message(models.Model):
    message_id = models.TextField(blank=False)
    account_type = models.CharField(max_length=20, choices=AccountType.choices, blank=False)

    # post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.message_id} : {self.account_type}'

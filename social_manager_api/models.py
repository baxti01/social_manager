import os.path

from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator
from django.db import models

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
    name = models.CharField(max_length=40, blank=False)
    type = models.CharField(max_length=20, choices=AccountType.choices, blank=False)
    token = models.TextField(blank=False, null=False)

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)


    def __str__(self):
        return f'{self.name} {self.type}'


class Post(models.Model):
    class ParseModeChoices(models.TextChoices):
        DEFAULT = "DEFAULT"
        MARKDOWN = "MARKDOWN"
        HTML = "HTML"
        DISABLED = "DISABLED"

    title = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    hash_tag = models.TextField(blank=True)
    photo = models.ImageField(
        upload_to=get_upload_path,
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg'])]
    )
    video = models.FileField(
        upload_to=get_upload_path,
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['mp4', 'mov'])]
    )
    parse_mode = models.CharField(
        max_length=20,
        choices=ParseModeChoices.choices,
        blank=False,
        null=False,
        default=ParseModeChoices.DEFAULT
    )

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    accounts = models.ManyToManyField(Account)
    chats = models.ManyToManyField("Chat")
    message_ids = models.ManyToManyField("Message")

    def __str__(self):
        return self.title


class Chat(models.Model):
    name = models.CharField(max_length=50, blank=True)
    username = models.CharField(max_length=60, blank=True, null=True)
    chat_id = models.CharField(max_length=255, unique=True)

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    account = models.ForeignKey(Account, related_name='chats', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.name}: {self.account.type}'


class Message(models.Model):
    message_id = models.TextField(blank=False)

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.message_id}: {self.account.type}'

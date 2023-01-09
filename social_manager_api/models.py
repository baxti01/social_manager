import os.path

from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator

User = get_user_model()


def get_upload_path(instance, filename):
    return os.path.join(
        f'{instance.user_id}',
        f'{instance.account_id}',
        filename
    )


class Account(models.Model):
    class AccountType(models.TextChoices):
        TIK_TOK = 'TikTok'
        INSTAGRAM = 'Instagram'
        # FACEBOOK = 'Facebook'
        TELEGRAM = 'Telegram'
        # VK = 'Vk'

    type = models.CharField(max_length=20, choices=AccountType.choices, blank=False)
    token = models.TextField(blank=False, null=False)

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)


class Post(models.Model):
    title = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    hash_tag = models.TextField(blank=True)
    image = models.ImageField(upload_to=get_upload_path, blank=True, null=True)
    video = models.FileField(
        upload_to=get_upload_path,
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['mp4', 'mov'])]
    )

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)

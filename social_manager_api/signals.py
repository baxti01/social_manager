from django.db.models.signals import post_delete
from django.dispatch import receiver

from social_manager_api.models import Post


@receiver(post_delete, sender=Post)
def delete_files(sender, instance: Post, **kwargs):
    if instance.photo:
        instance.photo.delete(False)

    if instance.video:
        instance.video.delete(False)
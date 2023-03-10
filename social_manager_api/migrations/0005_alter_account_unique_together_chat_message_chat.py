# Generated by Django 4.1.4 on 2023-01-28 15:06

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('social_manager_api', '0004_rename_image_post_photo_alter_post_parse_mode'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='account',
            unique_together={('type', 'user')},
        ),
        migrations.CreateModel(
            name='Chat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('chat_id', models.TextField()),
                ('account_type', models.CharField(choices=[('TikTok', 'Tik Tok'), ('Instagram', 'Instagram'), ('Telegram', 'Telegram')], max_length=20)),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='social_manager_api.post')),
            ],
        ),
        migrations.AddField(
            model_name='message',
            name='chat',
            field=models.ForeignKey(default=123, on_delete=django.db.models.deletion.CASCADE, to='social_manager_api.chat'),
            preserve_default=False,
        ),
    ]

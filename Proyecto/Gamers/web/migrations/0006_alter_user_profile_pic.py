# Generated by Django 4.0.6 on 2022-07-15 13:07

from django.db import migrations, models
import web.models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0005_alter_user_profile_pic'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='profile_pic',
            field=models.ImageField(blank=True, default='profile/default.png', help_text='Profile pic', null=True, upload_to=web.models.User.image_upload_to),
        ),
    ]

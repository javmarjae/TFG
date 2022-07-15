# Generated by Django 4.0.6 on 2022-07-15 12:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0002_alter_gamer_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='profile_pic',
            field=models.ImageField(blank=True, default='img/profile/default.png', help_text='Profile pic', null=True, upload_to='media/profile'),
        ),
    ]

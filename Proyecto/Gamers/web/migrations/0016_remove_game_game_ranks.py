# Generated by Django 4.0.6 on 2023-03-17 12:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0015_alter_clan_profile_pic'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='game',
            name='game_ranks',
        ),
    ]

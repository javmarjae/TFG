# Generated by Django 4.0.6 on 2023-04-11 21:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0021_report'),
    ]

    operations = [
        migrations.AddField(
            model_name='report',
            name='checked',
            field=models.BooleanField(default=False),
        ),
    ]

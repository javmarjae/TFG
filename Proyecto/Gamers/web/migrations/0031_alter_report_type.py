# Generated by Django 4.0.6 on 2023-04-13 13:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0030_alter_clan_join_date_alter_report_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='report',
            name='type',
            field=models.CharField(choices=[('he', 'Help'), ('ve', 'Verification'), ('bu', 'Bugs and errors'), ('cl', 'Clan'), ('us', 'User'), ('ac', 'Account')], default='he', help_text='TypeReport', max_length=2),
        ),
    ]

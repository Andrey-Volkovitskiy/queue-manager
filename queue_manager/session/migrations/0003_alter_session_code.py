# Generated by Django 4.2.4 on 2023-09-22 10:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('session', '0002_session_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='session',
            name='code',
            field=models.CharField(max_length=15, verbose_name='Code'),
        ),
    ]

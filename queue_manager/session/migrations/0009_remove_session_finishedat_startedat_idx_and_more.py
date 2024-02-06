# Generated by Django 4.2.4 on 2024-02-06 14:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('session', '0008_remove_session_finished_at_idx_and_more'),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name='session',
            name='finishedat_startedat_idx',
        ),
        migrations.AddIndex(
            model_name='session',
            index=models.Index(fields=['finished_at'], name='finished_at_idx'),
        ),
    ]

# Generated by Django 4.2.4 on 2024-02-06 08:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('status', '0006_alter_status_code_status_ticket_assignedat_code_idx'),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name='status',
            name='ticket_assignedat_code_idx',
        ),
        migrations.AddIndex(
            model_name='status',
            index=models.Index(fields=['ticket', '-assigned_at', 'code'], name='ticket_assignedat_code_idx'),
        ),
    ]

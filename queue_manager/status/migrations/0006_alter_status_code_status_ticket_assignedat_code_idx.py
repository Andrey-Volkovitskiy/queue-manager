# Generated by Django 4.2.4 on 2024-02-06 07:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('status', '0005_alter_status_assigned_to'),
    ]

    operations = [
        migrations.AlterField(
            model_name='status',
            name='code',
            field=models.CharField(choices=[('U', 'Unassigned'), ('P', 'Processing'), ('C', 'Completed'), ('R', 'Redirected'), ('M', 'Missed')], max_length=1, verbose_name='Status code'),
        ),
        migrations.AddIndex(
            model_name='status',
            index=models.Index(fields=['ticket', 'assigned_at', 'code'], name='ticket_assignedat_code_idx'),
        ),
    ]

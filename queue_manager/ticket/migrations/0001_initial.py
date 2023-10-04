# Generated by Django 4.2.4 on 2023-10-04 11:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('task', '0003_alter_task_description_alter_task_letter_code_and_more'),
        ('session', '0005_alter_session_finished_at_alter_session_finished_by'),
    ]

    operations = [
        migrations.CreateModel(
            name='Ticket',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=6, unique=True, verbose_name='Alphanumeric code')),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='session.session', verbose_name='Session')),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='task.task', verbose_name='Task')),
            ],
        ),
    ]

# Generated by Django 4.2.4 on 2023-10-12 08:32

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('ticket', '0002_alter_ticket_code_ticket_unique_code_in_session'),
    ]

    operations = [
        migrations.CreateModel(
            name='Status',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=1, verbose_name='Status code')),
                ('assigned_at', models.DateTimeField(auto_now_add=True, verbose_name='Assigned at')),
                ('assigned_by', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.PROTECT, related_name='assigned_by', to=settings.AUTH_USER_MODEL, verbose_name='Assigned by')),
                ('assigned_to', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.PROTECT, related_name='assigned_to', to=settings.AUTH_USER_MODEL, verbose_name='Assigned to')),
                ('ticket', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='ticket.ticket', verbose_name='Ticket')),
            ],
        ),
    ]
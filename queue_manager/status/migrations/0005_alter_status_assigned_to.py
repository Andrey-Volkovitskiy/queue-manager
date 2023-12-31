# Generated by Django 4.2.4 on 2023-11-17 11:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_alter_operator_options'),
        ('status', '0004_alter_status_assigned_to'),
    ]

    operations = [
        migrations.AlterField(
            model_name='status',
            name='assigned_to',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='assigned_to', to='user.operator', verbose_name='Assigned to'),
        ),
    ]

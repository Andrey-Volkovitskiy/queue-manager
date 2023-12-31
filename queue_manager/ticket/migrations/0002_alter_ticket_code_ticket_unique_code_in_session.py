# Generated by Django 4.2.4 on 2023-10-04 11:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ticket', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ticket',
            name='code',
            field=models.CharField(max_length=6, verbose_name='Alphanumeric code'),
        ),
        migrations.AddConstraint(
            model_name='ticket',
            constraint=models.UniqueConstraint(fields=('code', 'session'), name='unique_code_in_session'),
        ),
    ]

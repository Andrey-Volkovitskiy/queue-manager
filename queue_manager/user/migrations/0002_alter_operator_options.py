# Generated by Django 4.2.4 on 2023-11-03 11:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='operator',
            options={'permissions': [('pretend_operator', 'Can serve tickets pretending to be any of the operators')]},
        ),
    ]
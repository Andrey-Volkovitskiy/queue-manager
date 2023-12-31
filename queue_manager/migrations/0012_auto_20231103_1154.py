# Generated by Django 4.2.4 on 2023-11-03 11:54

from django.db import migrations
from django.contrib.auth.models import Group, User, Permission
from django.contrib.contenttypes.models import ContentType
from queue_manager.default_db_data import DefaultDBData


def create_groups():
    for group in DefaultDBData.groups.values():
        if not Group.objects.filter(name=group).exists():
            Group.objects.create(name=group)


def create_default_supervisor():
    is_default_supervisor_exists = User.objects.filter(
        username=DefaultDBData.default_supervisor['username']).exists()
    if not is_default_supervisor_exists:
        sprvsr = User.objects.create_user(**DefaultDBData.default_supervisor)
        sprvsr.groups.set((
            Group.objects.get(name=DefaultDBData.groups['SUPERVISORS']), ))


def add_supervisor_permissions():
    permission_id_list = []
    for perm in DefaultDBData.permissions_for_supervisors:
        if '.' in perm:
            app_name, perm_code = perm.split('.')
            content_type = ContentType.objects.filter(
                app_label=app_name).last()
            permission = Permission.objects.filter(
                content_type=content_type,
                codename=perm_code,
                ).last()
        else:
            permission = Permission.objects.filter(codename=perm).last()
        if permission:
            permission_id_list.append(permission.id)
    supervisors = Group.objects.get(name=DefaultDBData.groups['SUPERVISORS'])
    supervisors.permissions.set(permission_id_list)


def init_db(apps, schema_editor):
    create_groups()
    create_default_supervisor()
    add_supervisor_permissions()


class Migration(migrations.Migration):

    dependencies = [
        ('queue_manager', '0011_auto_20231031_1331'),
    ]

    operations = [
        migrations.RunPython(init_db),
    ]

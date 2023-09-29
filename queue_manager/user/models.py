from django.db import models
from django.contrib.auth.models import User, Group


def user_fullname_patch(self):
    return f"{self.first_name} {self.last_name}"


User.__str__ = user_fullname_patch


class SupervisorManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(
            groups=(Group.objects.get(name='supervisors')))


class Supervisor(User):
    class Meta:
        proxy = True

    objects = SupervisorManager()


class OperatorManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(
            groups=(Group.objects.get(name='operators')))


class Operator(User):
    class Meta:
        proxy = True

    objects = OperatorManager()

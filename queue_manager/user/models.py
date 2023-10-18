from django.contrib.auth.models import User, Group, UserManager


def user_fullname_patch(self):
    return f"{self.first_name} {self.last_name}"


User.__str__ = user_fullname_patch


class SupervisorManager(UserManager):
    def get_queryset(self):
        return super().get_queryset().filter(
            groups=(Group.objects.get(name='supervisors')))


class Supervisor(User):
    class Meta:
        proxy = True

    objects = SupervisorManager()


class OperatorManager(UserManager):
    def get_queryset(self):
        return super().get_queryset().filter(
            groups=(Group.objects.get(name='operators')))


class Operator(User):
    class Meta:
        proxy = True

    objects = OperatorManager()

    def save(self, *args, **kwargs):
        just_created = self.id is None
        super().save(*args, **kwargs)
        if just_created:
            self.groups.add(Group.objects.get(name='operators'))

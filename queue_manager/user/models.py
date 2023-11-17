from django.contrib.auth.models import User, Group, UserManager
import sys


def user_fullname_patch(self):
    return f"{self.first_name} {self.last_name}"


User.__str__ = user_fullname_patch
User.name = User.username


class SupervisorManager(UserManager):
    def get_queryset(self):
        return super().get_queryset().filter(
            groups=(Group.objects.get(name='supervisors')),
            is_active=True)


class Supervisor(User):
    class Meta:
        proxy = True

    objects = SupervisorManager()


class OperatorManager(UserManager):
    def get_queryset(self):
        return super().get_queryset().filter(
            groups=(Group.objects.get(name='operators')),
            is_active=True)


class Operator(User):
    class Meta:
        proxy = True
        permissions = [(
            "pretend_operator",
            "Can serve tickets pretending to be any of the operators"), ]

    objects = OperatorManager()

    @property
    def is_servicing(self):
        return self.service_set.filter(is_servicing=True).exists()

    @property
    def last_assigned_ticket(self):
        from queue_manager.status.models import Status
        last_processing_status = self.assigned_to.filter(
            code=Status.objects.Codes.PROCESSING).last()
        if last_processing_status:
            return last_processing_status.ticket

    @property
    def current_ticket(self):  # TODO Optimize request
        from queue_manager.status.models import Status
        if self.last_assigned_ticket and (
                self.last_assigned_ticket.status_set.last(
                ).code == Status.objects.Codes.PROCESSING):
            return self.last_assigned_ticket

    @property
    def is_free(self):
        return False if self.current_ticket else True

    def save(self, *args, **kwargs):
        '''Adds just created user to "operators" group
        and fixes pytest "pk=1' issue'''
        just_created = self.id is None
        if just_created and "pytest" in sys.modules:
            max_pk = User.objects.last().id
            self.id = max_pk + 1
        super().save(*args, **kwargs)
        if just_created:
            self.groups.add(Group.objects.get(name='operators'))

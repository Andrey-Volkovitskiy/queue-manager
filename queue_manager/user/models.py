from django.contrib.auth.models import User, Group, UserManager
from django.db.models import OuterRef, Subquery
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
        last_processing_status = Status.objects.filter(
            code=Status.objects.Codes.PROCESSING,
            assigned_to=self
            ).last()
        if last_processing_status:
            return last_processing_status.ticket

    @property
    def current_ticket(self):
        from queue_manager.status.models import Status
        from queue_manager.ticket.models import Ticket

        last_assigned_ticket = Subquery(
            Ticket.objects.filter(
                status__assigned_to=self,
                status__code=Status.objects.Codes.PROCESSING
                ).order_by('-status__assigned_at').values('id')[:1])

        last_status_code = Subquery(Status.objects.filter(
            ticket=OuterRef('id')).order_by('-assigned_at').values(
                'code')[:1])

        return Ticket.objects\
            .filter(id=last_assigned_ticket)\
            .annotate(last_status_code=last_status_code)\
            .filter(last_status_code=Status.objects.Codes.PROCESSING)\
            .last()

    @property
    def is_free(self):
        if self.is_servicing and not self.current_ticket:
            return True
        return False

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

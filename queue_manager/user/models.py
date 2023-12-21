from django.contrib.auth.models import User, Group, UserManager
from django.db.models import OuterRef, Subquery
from queue_manager.default_db_data import DefaultDBData
import sys


def user_fullname_patch(self):
    return f"{self.first_name} {self.last_name}"


User.__str__ = user_fullname_patch
User.name = User.username


class SupervisorManager(UserManager):
    def get_queryset(self):
        return super().get_queryset().filter(
            groups=(Group.objects.get(
                name=DefaultDBData.groups['SUPERVISORS'])),
            is_active=True)


class Supervisor(User):
    class Meta:
        proxy = True

    objects = SupervisorManager()


class OperatorManager(UserManager):
    def get_queryset(self):
        return super().get_queryset().filter(
            groups=(Group.objects.get(
                name=DefaultDBData.groups['OPERATORS'])),
            is_active=True)


class Operator(User):
    class Meta:
        proxy = True
        permissions = [(
            "pretend_operator",
            "Can serve tickets pretending to be any of the operators"), ]
        ordering = ['first_name', 'last_name']

    objects = OperatorManager()

    @property
    def is_servicing(self):
        return self.service_set.filter(is_servicing=True).exists()

    # TODO Add explain(), select_related/prefetch and defer/only
    # contains, F, Q, Subquery
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
            Ticket.objects
            .filter(
                status__assigned_to=self,
                status__code=Status.objects.Codes.PROCESSING)
            .order_by('-status__assigned_at')
            .values('id')[:1])

        last_status_code = Subquery(
            Status.objects
            .filter(ticket=OuterRef('id'))
            .order_by('-assigned_at')
            .values('code')[:1])

        last_status_assigned_to = Subquery(
            Status.objects
            .filter(ticket=OuterRef('id'))
            .order_by('-assigned_at')
            .values('assigned_to')[:1])

        return Ticket.objects\
            .filter(id=last_assigned_ticket)\
            .annotate(
                last_status_code=last_status_code,
                last_status_assigned_to=last_status_assigned_to)\
            .filter(
                last_status_code=Status.objects.Codes.PROCESSING,
                last_status_assigned_to=self)\
            .last()

    @property
    def is_free(self):
        if self.is_servicing and not self.current_ticket:
            return True
        return False

    @property
    def primary_task(self):
        from queue_manager.task.models import Service
        return self.task_set\
            .filter(
                service__is_servicing=True,
                service__priority_for_operator=Service.HIGHEST_PRIORITY)\
            .last()

    @property
    def secondary_tasks(self):
        from queue_manager.task.models import Service
        return self.task_set\
            .filter(
                service__is_servicing=True,
                service__priority_for_operator__lt=Service.HIGHEST_PRIORITY)\
            .order_by('letter_code')

    @property
    def count_tickets_completed(self):
        from queue_manager.ticket.models import Ticket
        from queue_manager.session.models import Session
        from queue_manager.status.models import Status

        last_status_code = Subquery(
            Status.objects
            .filter(ticket=OuterRef('id'))
            .order_by('-assigned_at')
            .values('code')[:1])

        last_status_assigned_by = Subquery(
            Status.objects
            .filter(ticket=OuterRef('id'))
            .order_by('-assigned_at')
            .values('assigned_by')[:1])

        return Ticket.objects\
            .filter(
                session=Session.objects.get_current_session(),
                status__code=Status.objects.Codes.COMPLETED,
                status__assigned_by=self)\
            .annotate(
                last_status_code=last_status_code,
                last_status_assigned_by=last_status_assigned_by)\
            .filter(
                last_status_code=Status.objects.Codes.COMPLETED,
                last_status_assigned_by=self)\
            .count()

    def get_personal_tickets(self, limit=None):
        '''Returns QuerySet with personal tickets assigned to the operator

        Arguments:
        limit - max numer of returned tickets'''
        from queue_manager.ticket.models import Ticket
        from queue_manager.status.models import Status

        last_status_code = Subquery(
            Status.objects
            .filter(ticket=OuterRef('id'))
            .order_by('-assigned_at')
            .values('code')[:1])

        last_status_assigned_to = Subquery(
            Status.objects
            .filter(ticket=OuterRef('id'))
            .order_by('-assigned_at')
            .values('assigned_to')[:1])

        last_status_assigned_at = Subquery(
            Status.objects
            .filter(ticket=OuterRef('id'))
            .order_by('-assigned_at')
            .values('assigned_at')[:1])

        return Ticket.objects\
            .filter(
                status__code=Status.objects.Codes.REDIRECTED,
                status__assigned_to=self)\
            .annotate(
                last_status_code=last_status_code,
                last_status_assigned_to=last_status_assigned_to)\
            .filter(
                last_status_code=Status.objects.Codes.REDIRECTED,
                last_status_assigned_to=self)\
            .annotate(last_status_assigned_at=last_status_assigned_at)\
            .order_by('last_status_assigned_at')[: limit]

    def get_primary_tickets(self, limit=None, primary_task_id=None):
        '''Returns QuerySet with primary tickets
        which can be assigned to the operator

        Arguments:
        limit - max numer of returned tickets
        primary_task - only used to test this method'''
        from queue_manager.ticket.models import Ticket
        from queue_manager.task.models import Service
        from queue_manager.status.models import Status

        last_status_code = Subquery(Status.objects.filter(
            ticket=OuterRef('id')).order_by('-assigned_at').values(
                'code')[:1])

        last_status_assigned_at = Subquery(Status.objects.filter(
            ticket=OuterRef('id')).order_by('-assigned_at').values(
                'assigned_at')[:1])

        if primary_task_id is None:
            primary_task_id = Subquery(
                Service.objects.filter(
                    operator=self,
                    is_servicing=True,
                    priority_for_operator=9
                ).values('task_id')[:1])

        return Ticket.objects.filter(task__id=primary_task_id)\
            .annotate(
                last_status_code=last_status_code,
                last_status_assigned_at=last_status_assigned_at)\
            .filter(last_status_code=Status.objects.Codes.UNASSIGNED)\
            .order_by('last_status_assigned_at')[: limit]

    def get_secondary_tickets(self, limit=None, secondery_tasks_ids=None):
        '''Returns QuerySet with secondary tickets
        which can be assigned to the operator

        Arguments:
        limit - max numer of returned tickets
        secondery_tasks_ids - only used to test this method'''
        from queue_manager.ticket.models import Ticket
        from queue_manager.task.models import Service
        from queue_manager.status.models import Status

        last_status_code = Subquery(Status.objects.filter(
            ticket=OuterRef('id')).order_by('-assigned_at').values(
                'code')[:1])

        last_status_assigned_at = Subquery(Status.objects.filter(
            ticket=OuterRef('id')).order_by('-assigned_at').values(
                'assigned_at')[:1])

        if secondery_tasks_ids is None:
            secondery_tasks_ids = Subquery(
                Service.objects.filter(
                    operator=self,
                    is_servicing=True,
                    priority_for_operator__lt=Service.HIGHEST_PRIORITY
                ).values_list('task_id', flat=True))

        return Ticket.objects.filter(task__id__in=secondery_tasks_ids)\
            .annotate(
                last_status_code=last_status_code,
                last_status_assigned_at=last_status_assigned_at)\
            .filter(last_status_code=Status.objects.Codes.UNASSIGNED)\
            .order_by('last_status_assigned_at')[: limit]

    def save(self, *args, **kwargs):
        '''Adds just created user to "operators" group
        and fixes pytest "pk=1' issue'''  # TODO Fix it
        just_created = self.id is None
        if just_created and "pytest" in sys.modules:
            max_pk = User.objects.last().id
            self.id = max_pk + 1
        super().save(*args, **kwargs)
        if just_created:
            self.groups.add(Group.objects.get(
                name=DefaultDBData.groups['OPERATORS']))

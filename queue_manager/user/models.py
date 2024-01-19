from django.contrib.auth.models import User, Group, UserManager
from django.db.models import Subquery, OuterRef, Func, F
from queue_manager.default_db_data import DefaultDBData
import sys


def user_fullname_patch(self):
    return f"{self.first_name} {self.last_name}"


User.__str__ = user_fullname_patch
User.name = User.username


class SupervisorManager(UserManager):
    def get_queryset(self):
        return super().get_queryset()\
            .filter(
                groups__name=DefaultDBData.groups['SUPERVISORS'],
                is_active=True)


class Supervisor(User):
    '''Manages operators, tasks and sessions'''
    class Meta:
        proxy = True

    objects = SupervisorManager()


class OperatorManager(UserManager):
    def get_queryset(self):
        return super().get_queryset()\
            .filter(
                groups__name=DefaultDBData.groups['OPERATORS'],
                is_active=True)


class Operator(User):
    '''Services tickets'''
    class Meta:
        proxy = True
        permissions = [(
            "pretend_operator",
            "Can serve tickets pretending to be any of the operators"), ]
        ordering = ['first_name', 'last_name']

    objects = OperatorManager()

    @property
    def is_servicing(self):
        '''Is the operator currently sericing any task?'''
        return self.service_set.filter(priority__gt=0).exists()

    @property
    def current_ticket(self):
        '''Returns ticket that is currently being processed by the operator'''
        from queue_manager.status.models import Status
        from queue_manager.ticket.models import Ticket

        last_assigned_ticket_id = Subquery(
            Ticket.objects
            .filter(
                status__assigned_to=self,
                status__code=Status.PROCESSING.code)
            .order_by('-status__assigned_at')
            .values('id')[:1])

        return Ticket.objects\
            .annotate(
                last_status_code=Ticket.subq_last_status_code(),
                last_status_assigned_to=Ticket.subq_last_status_assigned_to())\
            .filter(
                id=last_assigned_ticket_id,
                last_status_code=Status.PROCESSING.code,
                last_status_assigned_to=self)\
            .last()

    @staticmethod
    def subq_current_ticket_code():
        '''Returns subquery with current ticket code for the operator'''
        from queue_manager.status.models import Status
        from queue_manager.ticket.models import Ticket
        last_assigned_ticket_id = Subquery(
            Ticket.objects
            .filter(
                status__assigned_to=OuterRef(OuterRef('id')),
                status__code=Status.PROCESSING.code)
            .order_by('-status__assigned_at')
            .values('id')[:1])

        return Subquery(
            Ticket.objects
            .annotate(
                last_status_code=Ticket.subq_last_status_code(),
                last_status_assigned_to=Ticket.subq_last_status_assigned_to())
            .filter(
                id=last_assigned_ticket_id,
                last_status_code=Status.PROCESSING.code,
                last_status_assigned_to=OuterRef('id'))
            .order_by()
            .values('code')[:1])

    @property
    def is_free(self):
        '''Is the operator is available to get a new ticket for processing?'''
        if self.is_servicing and not self.current_ticket:
            return True
        return False

    @property
    def primary_task(self):
        '''Returns a primary task
        that is currently being serviced by the operator'''
        from queue_manager.task.models import Service
        return self.task_set\
            .filter(service__priority=Service.HIGHEST_PRIORITY)\
            .only('name', 'letter_code')\
            .last()

    @property
    def secondary_tasks(self):
        '''Returns secondary tasks
        that are currently being serviced by the operator'''
        from queue_manager.task.models import Service
        return self.task_set\
            .filter(
                service__priority__lt=Service.HIGHEST_PRIORITY,
                service__priority__gt=Service.NOT_IN_SERVICE)\
            .only('name', 'letter_code')\
            .order_by('letter_code')

    @property
    def count_tickets_completed(self):
        '''Returns a number of tickets completed by the operator
        during the current session'''
        from queue_manager.ticket.models import Ticket
        from queue_manager.session.models import Session
        from queue_manager.status.models import Status

        return Ticket.objects\
            .filter(
                session__id=Session.objects.subq_current_session_id(),)\
            .annotate(
                last_status_code=Ticket.subq_last_status_code(),
                last_status_assigned_by=Ticket.subq_last_status_assigned_by())\
            .filter(
                last_status_code=Status.COMPLETED.code,
                last_status_assigned_by=self)\
            .count()

    @staticmethod
    def subq_count_tickets_completed():
        '''Returns a subquery with the number of tickets
        completed by the operator during the current session'''
        from queue_manager.ticket.models import Ticket
        from queue_manager.session.models import Session
        from queue_manager.status.models import Status

        return Subquery(
            Ticket.objects
            .filter(
                session__id=Session.objects.subq_current_session_id(),)
            .annotate(
                last_status_code=Ticket.subq_last_status_code(),
                last_status_assigned_by=Ticket.subq_last_status_assigned_by())
            .filter(
                last_status_code=Status.COMPLETED.code,
                last_status_assigned_by=OuterRef('id'))
            .annotate(count=Func(F('id'), function='Count'))
            .values('count'))

    def get_tickets_with_status(self, status_code, limit=None):
        '''Returns tickets with specific last status
        assigned by the operator.

        Arguments:
        status_code - filter criteria
        limit - max numer of returned tickets'''
        from queue_manager.ticket.models import Ticket
        from queue_manager.session.models import Session

        return Ticket.objects\
            .filter(session=Session.objects.subq_last_session_id())\
            .annotate(
                last_status_code=Ticket.subq_last_status_code(),
                last_status_assigned_by=Ticket.subq_last_status_assigned_by(),
                last_status_assigned_at=Ticket.subq_last_status_assigned_at())\
            .filter(
                last_status_assigned_by=self,
                last_status_code=status_code)\
            .order_by(
                '-last_status_assigned_at')[:limit]

    def get_personal_tickets(self, limit=None):
        '''Returns personal tickets assigned to the operator

        Arguments:
        limit - max numer of returned tickets'''
        from queue_manager.ticket.models import Ticket
        from queue_manager.status.models import Status

        return Ticket.objects\
            .filter(
                status__code=Status.REDIRECTED.code,
                status__assigned_to=self)\
            .annotate(
                last_status_code=Ticket.subq_last_status_code(),
                last_status_assigned_to=Ticket.subq_last_status_assigned_to())\
            .filter(
                last_status_code=Status.REDIRECTED.code,
                last_status_assigned_to=self)\
            .annotate(
                last_status_assigned_at=Ticket.subq_last_status_assigned_at())\
            .order_by('last_status_assigned_at')[: limit]

    def get_primary_tickets(self, limit=None, primary_task_id=None):
        '''Returns primary tickets which can be assigned to the operator

        Arguments:
        limit - max numer of returned tickets
        primary_task_id - only used to test this method'''
        from queue_manager.ticket.models import Ticket
        from queue_manager.task.models import Service
        from queue_manager.status.models import Status

        prim_task_id = primary_task_id or Subquery(
                Service.objects
                .filter(
                    operator=self,
                    priority=Service.HIGHEST_PRIORITY)
                .values('task_id')[:1])

        return Ticket.objects\
            .filter(task__id=prim_task_id)\
            .annotate(
                last_status_code=Ticket.subq_last_status_code(),
                last_status_assigned_at=Ticket.subq_last_status_assigned_at())\
            .filter(last_status_code=Status.UNASSIGNED.code)\
            .order_by('last_status_assigned_at')[: limit]

    def get_secondary_tickets(self, limit=None, secondery_tasks_ids=None):
        '''Returns secondary tickets which can be assigned to the operator

        Arguments:
        limit - max numer of returned tickets
        secondery_tasks_ids - only used to test this method'''
        from queue_manager.ticket.models import Ticket
        from queue_manager.task.models import Service
        from queue_manager.status.models import Status

        scnd_tasks_ids = secondery_tasks_ids or Subquery(
                Service.objects
                .filter(
                    operator=self,
                    priority__lt=Service.HIGHEST_PRIORITY,
                    priority__gt=Service.NOT_IN_SERVICE)
                .values_list('task_id', flat=True))

        return Ticket.objects\
            .filter(task__id__in=scnd_tasks_ids)\
            .annotate(
                last_status_code=Ticket.subq_last_status_code(),
                last_status_assigned_at=Ticket.subq_last_status_assigned_at())\
            .filter(last_status_code=Status.UNASSIGNED.code)\
            .order_by('last_status_assigned_at')[: limit]

    def save(self, *args, **kwargs):
        '''Adds just created user to "operators" group
        and fixes pytest "pk=1' issue'''
        just_created = self.id is None
        if just_created and "pytest" in sys.modules:
            max_pk = User.objects.last().id
            self.id = max_pk + 1
        super().save(*args, **kwargs)
        if just_created:
            self.groups.add(Group.objects.get(
                name=DefaultDBData.groups['OPERATORS']))

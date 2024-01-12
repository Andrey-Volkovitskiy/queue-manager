from django.db import models
from queue_manager.models import SoftDeletionModel
from django.core.validators import RegexValidator
from queue_manager.session.models import Session
from queue_manager.user.models import Operator
from queue_manager.status.models import Status
from django.db.models import Subquery, OuterRef, Func, F


ITEM_NAME = 'task'


only_letters = RegexValidator(
    r'^[a-zA-Z]*$',
    'Only English letters are allowed.')


class CapitalizedCharField(models.CharField):
    '''A CharField with capitalized first character'''
    def get_prep_value(self, value):
        value = super().get_prep_value(value)
        if isinstance(value, str) and len(value) > 0:
            return value[0:1].upper() + value[1:]
        return value


class Task(SoftDeletionModel):
    name = CapitalizedCharField(
        max_length=75,
        verbose_name='Name'
    )
    description = CapitalizedCharField(
        max_length=200,
        blank=True,
        verbose_name='Description'
    )
    letter_code = CapitalizedCharField(
        max_length=1,
        verbose_name='Letter code',
        validators=[only_letters],
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Created at'
    )
    can_be_served_by = models.ManyToManyField(
        Operator,
        through='Service',
        blank=True,
    )

    def __str__(self):
        return f'{self.letter_code} - {self.name}'

    class Meta:
        constraints = [models.UniqueConstraint(
            fields=['letter_code'],
            condition=models.Q(deleted_at=None),
            name='unique_if_not_deleted'
        )]

    @property
    def primary_served_by(self) -> Operator:
        '''Returns operators who serve the task as primary.'''
        return self.can_be_served_by\
            .filter(service__priority=Service.HIGHEST_PRIORITY)\
            .order_by('first_name', 'last_name')

    @property
    def secondary_served_by(self) -> Operator:
        '''Returns operators who serve the task as secondary.'''
        return self.can_be_served_by\
            .filter(
                service__priority__lt=Service.HIGHEST_PRIORITY,
                service__priority__gt=Service.NOT_IN_SERVICE)\
            .order_by('first_name', 'last_name')

    @property
    def count_tickets_completed(self):
        '''Counts complited tickets for the task for current session'''
        from queue_manager.ticket.models import Ticket
        return self.ticket_set\
            .annotate(last_status_code=Ticket.subq_last_status_code())\
            .filter(
                session__id=Session.objects.subq_current_session_id(),
                last_status_code=Status.objects.Codes.COMPLETED)\
            .count()

    @staticmethod
    def subq_count_tickets_completed():
        '''Returns subquery that counts complited tickets
        for the task for current session'''
        from queue_manager.ticket.models import Ticket
        return Subquery(
            Ticket.objects
            .filter(task__id=OuterRef('id'))
            .annotate(last_status_code=Ticket.subq_last_status_code())
            .filter(
                session__id=Session.objects.subq_current_session_id(),
                last_status_code=Status.objects.Codes.COMPLETED)
            .annotate(count=Func(F('id'), function='Count'))
            .values('count'))

    @property
    def count_tickets_unprocessed(self):
        '''Counts unprocessed (U, P, R) tickets for the task
        for current session'''
        from queue_manager.ticket.models import Ticket
        return self.ticket_set\
            .annotate(last_status_code=Ticket.subq_last_status_code())\
            .filter(
                session__id=Session.objects.subq_current_session_id(),
                last_status_code__in=(
                    Status.objects.Codes.unprocessed_codes))\
            .count()

    @staticmethod
    def subq_count_tickets_unprocessed():
        '''Returns subquery that counts unprocessed (U, P, R) tickets
        for the task for current session'''
        from queue_manager.ticket.models import Ticket
        return Subquery(
            Ticket.objects
            .filter(task__id=OuterRef('id'))
            .annotate(last_status_code=Ticket.subq_last_status_code())
            .filter(
                session__id=Session.objects.subq_current_session_id(),
                last_status_code__in=(
                    Status.objects.Codes.unprocessed_codes))
            .annotate(count=Func(F('id'), function='Count'))
            .values('count'))


class Service(models.Model):
    '''If service record exists, than the operator have the authoriry
    to serve the task.
    If priority field is Null, the operator isn't currently
    servicing the task.'''
    NOT_IN_SERVICE = 0
    LOWEST_PRIORITY = 1
    HIGHEST_PRIORITY = 9

    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE
    )
    operator = models.ForeignKey(
        Operator,
        on_delete=models.CASCADE
    )
    priority = models.SmallIntegerField(
        default=NOT_IN_SERVICE
    )

    @property
    def is_servicing(self):
        return bool(self.priority)

from django.db import models
from django.core.validators import RegexValidator
from queue_manager.session.models import Session
from queue_manager.user.models import Operator
from queue_manager.status.models import Status
from django.db.models import OuterRef, Subquery


ITEM_NAME = 'task'


only_letters = RegexValidator(
    r'^[a-zA-Z]*$',
    'Only English letters are allowed.')


class CapitalizedCharField(models.CharField):
    def get_prep_value(self, value):
        value = super().get_prep_value(value)
        if isinstance(value, str) and len(value) > 0:
            return value[0:1].upper() + value[1:]
        return value


class Task(models.Model):
    name = CapitalizedCharField(
        max_length=75,
        unique=True,
        verbose_name='Name'
    )
    description = CapitalizedCharField(
        max_length=200,
        blank=True,
        verbose_name='Description'
    )
    letter_code = CapitalizedCharField(
        max_length=1,
        unique=True,
        verbose_name='Letter code',
        validators=[only_letters],
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Is active'
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

    @property
    def primary_served_by(self) -> Operator:
        return Operator.objects\
            .filter(
                service__task=self,
                service__is_servicing=True,
                service__priority_for_operator=Service.HIGHEST_PRIORITY)\
            .order_by('last_name', 'first_name')

    @property
    def secondary_served_by(self) -> Operator:
        return Operator.objects\
            .filter(
                service__task=self,
                service__is_servicing=True,
                service__priority_for_operator__lt=Service.HIGHEST_PRIORITY)\
            .order_by('last_name', 'first_name')

    @property
    def count_tickets_completed(self):
        last_status_code = Subquery(Status.objects.filter(
            ticket=OuterRef('id')).order_by('-assigned_at').values(
                'code')[:1])
        return self.ticket_set\
            .filter(session=Session.objects.get_current_session())\
            .annotate(last_status_code=last_status_code)\
            .filter(last_status_code=Status.objects.Codes.COMPLETED)\
            .count()

    @property
    def count_tickets_unprocessed(self):
        last_status_code = Subquery(Status.objects.filter(
            ticket=OuterRef('id')).order_by('-assigned_at').values(
                'code')[:1])
        return self.ticket_set\
            .filter(session=Session.objects.get_current_session())\
            .annotate(last_status_code=last_status_code)\
            .filter(last_status_code__in=(
                Status.objects.Codes.unprocessed_status_codes))\
            .count()


class Service(models.Model):
    '''If service record exists, than the operator have the authoriry
    to serve the task.
    If is_servicing flag is true, the operator is currently servicing the task
    with given priority.'''
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
    is_servicing = models.BooleanField(
        default=False
    )
    priority_for_operator = models.SmallIntegerField(
        null=True
    )

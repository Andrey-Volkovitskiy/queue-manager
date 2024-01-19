from collections import namedtuple
from django.db import models
from django.contrib.auth.models import User
from queue_manager.user.models import Operator


ITEM_NAME = 'status'


class StatusManager(models.Manager):
    class StatusErrors(Exception):
        pass

    class StatusFlowViolated(StatusErrors):
        '''Raised when attempt is made to change the ticket status
        not according to status change flow'''
        pass

    class NotEnoughArguments(StatusErrors):
        '''Raised when attempt is made to add new status
        without "assigned_to" or "assigned_by" argument'''
        pass

    def create_initial(self, ticket):
        '''Creates the initial status when creating a ticket'''
        return self.create(
            ticket=ticket,
            code=Status.UNASSIGNED.code)

    def create_additional(self, ticket, new_code,     # noqa C901
                          assigned_by=None, assigned_to=None):
        '''Creates 2nd / 3rd / ... statuses for the ticket
        and implements status lifecycle logic'''

        def _check_attrs_exist(attributes_dict, mandatory_attrs):
            for mandatory_attr in mandatory_attrs:
                try:
                    if attributes_dict[mandatory_attr] is None:
                        raise self.NotEnoughArguments
                except KeyError:
                    raise self.NotEnoughArguments

        attributes_dict = locals()
        last_code = self.filter(ticket=ticket).last().code
        current_status_option = Status.get_status_option_by_code(last_code)

        if not current_status_option or (
                new_code not in current_status_option.next_allowed_codes):
            raise self.StatusFlowViolated

        new_status_option = Status.get_status_option_by_code(new_code)
        _check_attrs_exist(attributes_dict,
                           new_status_option.mandatory_attributes)

        return self.create(
                ticket=ticket,
                code=new_code,
                assigned_by=assigned_by,
                assigned_to=assigned_to)


class Status(models.Model):
    '''The current state of the ticket described by its latest status.'''

    # STATUS OPTIONS
    StatusOption = namedtuple('StatusOption', [
        'code',
        'name',
        'next_allowed_codes',  # according to status lifecycle
        'mandatory_attributes',  # assigned_to or assigned_by
        'colour'  # for Bootstrap templates
    ])
    UNASSIGNED = StatusOption(
        code='U',
        name='Unassigned',
        next_allowed_codes=('P', ),
        mandatory_attributes=(),
        colour='secondary'
    )
    PROCESSING = StatusOption(
        code='P',
        name='Processing',
        next_allowed_codes=('C', 'M', 'R'),
        mandatory_attributes=('assigned_to', ),
        colour='success'
    )
    COMPLETED = StatusOption(
        code='C',
        name='Completed',
        next_allowed_codes=('R', ),
        mandatory_attributes=('assigned_by', ),
        colour='primary'
    )
    REDIRECTED = StatusOption(
        code='R',
        name='Redirected',
        next_allowed_codes=('P', ),
        mandatory_attributes=('assigned_to', 'assigned_by'),
        colour='danger'
    )
    MISSED = StatusOption(
        code='M',
        name='Missed',
        next_allowed_codes=('R', ),
        mandatory_attributes=('assigned_by', ),
        colour='warning'
    )

    ALL_STATUS_OPTIONS = (
        UNASSIGNED, PROCESSING, COMPLETED, REDIRECTED, MISSED)

    UNPROCESSED_CODES = (UNASSIGNED.code, PROCESSING.code, REDIRECTED.code)

    # FIELDS
    ticket = models.ForeignKey(
        'ticket.Ticket',
        on_delete=models.PROTECT,
        verbose_name='Ticket'
    )
    code = models.CharField(
        max_length=1,
        choices=((o.code, o.name) for o in ALL_STATUS_OPTIONS),
        verbose_name='Status code'
    )
    assigned_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Assigned at'
    )
    assigned_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        verbose_name='Assigned by',
        related_name='assigned_by',
        null=True,
    )
    assigned_to = models.ForeignKey(
        Operator,
        on_delete=models.PROTECT,
        verbose_name='Assigned to',
        related_name='assigned_to',
        null=True,
    )
    objects = StatusManager()

    @property
    def responsible(self):
        '''The operator currenlly responsihble for the status'''
        if self.code in (
                Status.PROCESSING.code,
                Status.REDIRECTED.code):
            return self.assigned_to
        elif self.code in (
                Status.MISSED.code,
                Status.COMPLETED.code):
            return self.assigned_by

    @property
    def name(self):
        '''Returns status name'''
        status_option = self.get_status_option_by_code(self.code)
        return status_option.name

    @property
    def colour(self):
        '''Returns status colour for Bootstrap templates'''
        status_option = self.get_status_option_by_code(self.code)
        return status_option.colour

    @staticmethod
    def get_status_option_by_code(status_code):
        for status_option in Status.ALL_STATUS_OPTIONS:
            if status_option.code == status_code:
                return status_option

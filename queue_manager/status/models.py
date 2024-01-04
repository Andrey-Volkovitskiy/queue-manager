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

    class Codes():
        '''Possible ticket statuses'''
        UNASSIGNED = 'U'
        PROCESSING = 'P'
        COMPLETED = 'C'
        REDIRECTED = 'R'
        MISSED = 'M'

        unprocessed_codes = (
            UNASSIGNED,
            PROCESSING,
            REDIRECTED
        )

    def create_initial(self, ticket):
        '''Creates the initial status when creating a ticket'''
        return self.create(
            ticket=ticket,
            code=self.Codes.UNASSIGNED
        )

    def create_additional(self, ticket, new_code: Codes,  # noqa: C901
                          assigned_by=None, assigned_to=None):
        '''Creates a new status for the ticket
        and implements status flow logic'''

        def _check_args(*args):
            for arg in args:
                if arg is None:
                    raise self.NotEnoughArguments

        def _create_new_status():
            return self.create(
                    ticket=ticket,
                    code=new_code,
                    assigned_by=assigned_by,
                    assigned_to=assigned_to
                )

        last_code = self.filter(ticket=ticket).last().code

        if last_code == self.Codes.UNASSIGNED:
            if new_code in (self.Codes.PROCESSING, ):
                _check_args((assigned_to, ))
                return _create_new_status()
            else:
                raise self.StatusFlowViolated

        elif last_code == self.Codes.PROCESSING:
            if new_code in (self.Codes.COMPLETED, self.Codes.MISSED,
                            self.Codes.REDIRECTED):
                _check_args((assigned_by, ))
                return _create_new_status()
            else:
                raise self.StatusFlowViolated

        elif last_code == self.Codes.COMPLETED:
            if new_code in (self.Codes.REDIRECTED, ):
                _check_args(assigned_by, assigned_to)
                return _create_new_status()
            else:
                raise self.StatusFlowViolated

        elif last_code == self.Codes.REDIRECTED:
            if new_code in (self.Codes.PROCESSING, ):
                _check_args((assigned_to, ))
                return _create_new_status()
            else:
                raise self.StatusFlowViolated

        elif last_code == self.Codes.MISSED:
            if new_code in (self.Codes.REDIRECTED, ):
                _check_args(assigned_by, assigned_to)
                return _create_new_status()
            else:
                raise self.StatusFlowViolated

        else:
            raise self.StatusFlowViolated


class Status(models.Model):
    ticket = models.ForeignKey(
        'ticket.Ticket',
        on_delete=models.PROTECT,
        verbose_name='Ticket'
    )
    code = models.CharField(
        max_length=1,
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
                StatusManager.Codes.PROCESSING,
                StatusManager.Codes.REDIRECTED):
            return self.assigned_to
        elif self.code in (
                StatusManager.Codes.MISSED,
                StatusManager.Codes.COMPLETED):
            return self.assigned_by

    @property
    def name(self):
        '''The status name based on code'''
        dic = StatusManager.Codes.__dict__
        name = {atr for atr in dic if dic[atr] == self.code}.pop()
        return name.capitalize()

    @property
    def colour(self):
        '''The status colour based on code'''
        if self.code == StatusManager.Codes.UNASSIGNED:
            return 'secondary'
        elif self.code == StatusManager.Codes.PROCESSING:
            return 'success'
        elif self.code == StatusManager.Codes.COMPLETED:
            return 'primary'
        elif self.code == StatusManager.Codes.REDIRECTED:
            return 'danger'
        elif self.code == StatusManager.Codes.MISSED:
            return 'warning'

from django.db import models
from queue_manager.task.models import Task
from queue_manager.session.models import Session


ITEM_NAME = 'ticket'
NUM_OF_DIGITS_IN_TICKET_CODE = 3


class TicketManager(models.Manager):

    class TicketErrors(Exception):
        pass

    class NoActiveSessionError(TicketErrors):
        '''Raised when attempt is made to create a new ticket
        while there is no active session'''
        pass

    def _get_new_ticket_code(self, session: Session, task: Task):
        last_ticket = Task.objects.filter(
            session=session, task=task).order_by('code').last()
        if last_ticket is None:
            new_ticket_number = 1
        else:
            last_ticket_number = int(last_ticket.code[1:])
            new_ticket_number = last_ticket_number + 1
        return task.letter_code + format(
            new_ticket_number, f'0{NUM_OF_DIGITS_IN_TICKET_CODE}d')

    def create_ticket(self, task: Task):
        '''Creates a new Ticket instance with properly filed fields'''
        current_session = Session.objects.get_current_session()
        if not current_session:
            raise self.NoActiveSessionError
        code = self._get_new_ticket_code(current_session, task)
        return self.create(
            code=code,
            session=current_session,
            task=task
        )


class Ticket(models.Model):
    code = models.CharField(
        max_length=6,
        verbose_name='Alphanumeric code'
    )
    task = models.ForeignKey(
        Task,
        on_delete=models.PROTECT,
        verbose_name='Task'
    )
    session = models.ForeignKey(
        Session,
        on_delete=models.PROTECT,
        verbose_name='Session'
    )
    objects = TicketManager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['code', 'session'],
                name='unique_code_in_session')
        ]

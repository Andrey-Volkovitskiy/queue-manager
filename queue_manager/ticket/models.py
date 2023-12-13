import random
from django.db import models
from queue_manager.task.models import Task
from queue_manager.session.models import Session
from queue_manager.status.models import Status
from django.db.models import OuterRef, Subquery
from queue_manager.user.models import Operator


ITEM_NAME = 'ticket'
NUM_OF_DIGITS_IN_TICKET_CODE = 3


class TicketManager(models.Manager):
    def _get_new_ticket_code(self, session: Session, task: Task):
        last_ticket = Ticket.objects.filter(
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
            raise Session.objects.NoActiveSessionsError
        code = self._get_new_ticket_code(current_session, task)
        new_ticket = self.create(
            code=code,
            session=current_session,
            task=task
        )
        new_ticket.status_set.create_initial(ticket=new_ticket)
        QManager.general_ticket_appeared(new_ticket)
        return new_ticket


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

    @property
    def responsible(self):
        '''The operator currenlly responsible for the ticket'''
        last_status = self.status_set.last
        if last_status:
            return last_status.responsible

    @property
    def num_tickets_ahead(self):
        '''The number of unassidned tickets in front the ticket'''
        last_status_code = Subquery(
            Status.objects
            .filter(ticket=OuterRef('id'))
            .order_by('-id')
            .values('code')[:1])

        return self._meta.model.objects\
            .filter(
                session=Session.objects.get_current_session(),
                task=self.task,
                id__lt=self.id,)\
            .annotate(last_status_code=last_status_code)\
            .filter(last_status_code=Status.objects.Codes.UNASSIGNED)\
            .count()

    def __str__(self):
        return self.code

    def assign_to_operator(self, operator):
        Status.objects.create_additional(
            ticket=self,
            new_code=Status.objects.Codes.PROCESSING,
            assigned_to=operator,
        )

    def mark_completed(self):
        processing_operator = self.status_set.filter(
            code=Status.objects.Codes.PROCESSING).last().assigned_to
        Status.objects.create_additional(
            ticket=self,
            new_code=Status.objects.Codes.COMPLETED,
            assigned_by=processing_operator,
        )
        QManager.free_operator_appeared(operator=processing_operator)

    def mark_missed(self):
        processing_operator = self.status_set.filter(
            code=Status.objects.Codes.PROCESSING).last().assigned_to
        Status.objects.create_additional(
            ticket=self,
            new_code=Status.objects.Codes.MISSED,
            assigned_by=processing_operator,
        )
        QManager.free_operator_appeared(operator=processing_operator)

    def redirect(self, redirect_to: Operator):
        processing_operator = self.status_set.filter(
            code=Status.objects.Codes.PROCESSING).last().assigned_to
        Status.objects.create_additional(
            ticket=self,
            new_code=Status.objects.Codes.REDIRECTED,
            assigned_by=processing_operator,
            assigned_to=redirect_to
        )
        QManager.personal_ticket_appeared(
            ticket=self,
            assigned_to=redirect_to
        )
        if processing_operator.is_free:
            QManager.free_operator_appeared(operator=processing_operator)


class QManager:
    @staticmethod  # Personal - ticket redirected by someone to the operator
    def personal_ticket_appeared(ticket: Ticket, assigned_to: Operator):
        if assigned_to.is_free:
            ticket.assign_to_operator(assigned_to)

    @classmethod  # General - ticket just issued to a client
    def general_ticket_appeared(cls, ticket: Ticket):
        task = ticket.task
        free_operator = cls._get_next_free_operator(task)
        if free_operator:
            ticket.assign_to_operator(free_operator)

    @classmethod
    def free_operator_appeared(cls, operator: Operator):
        if not operator.is_servicing:
            return
        personal_ticket = cls._get_next_personal_ticket(operator)
        if personal_ticket:
            return personal_ticket.assign_to_operator(operator)

        general_ticket = cls._get_next_primary_ticket(operator) or (
            cls._get_next_secondary_ticket(operator))
        if general_ticket:
            return general_ticket.assign_to_operator(operator)

    @staticmethod
    def _get_next_personal_ticket(operator: Operator) -> Ticket:
        first_ticket_list = operator.get_personal_tickets(limit=1)
        if len(first_ticket_list) > 0:
            return first_ticket_list[0]

    @staticmethod
    def _get_next_primary_ticket(
                operator: Operator, primary_task_id=None) -> Ticket:
        '''primary_task is only used to test this method'''

        list_with_first_ticket = operator.get_primary_tickets(
            limit=1,
            primary_task_id=primary_task_id)
        if len(list_with_first_ticket) > 0:
            return list_with_first_ticket[0]

    @staticmethod
    def _get_next_secondary_ticket(
            operator: Operator, secondery_tasks_ids=None) -> Ticket:
        '''secondery_tasks_ids is only used to test this method'''

        list_with_first_ticket = operator.get_secondary_tickets(
            limit=1,
            secondery_tasks_ids=secondery_tasks_ids)
        if len(list_with_first_ticket) > 0:
            return list_with_first_ticket[0]

    @staticmethod
    def _get_free_operators(task: Task):
        '''Returns all operators which:
        - currently is_servicing the task
        - don't currently have ticket in processing'''
        last_assigned_ticket = Subquery(
            Ticket.objects
            .filter(
                status__assigned_to=OuterRef(OuterRef('id')),
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

        current_ticket = Subquery(
            Ticket.objects
            .filter(id=last_assigned_ticket)
            .annotate(
                last_status_code=last_status_code,
                last_status_assigned_to=last_status_assigned_to)
            .filter(
                last_status_code=Status.objects.Codes.PROCESSING,
                last_status_assigned_to=OuterRef('id'))
            .values('id'))

        processing_operators = Subquery(
            Operator.objects
            .filter(id=OuterRef('id'))
            .annotate(current_ticket=current_ticket)
            .filter(current_ticket__isnull=False)
            .values('id'))

        free_operators = task.can_be_served_by.filter(
            service__is_servicing=True).exclude(id__in=processing_operators)

        return free_operators

    @classmethod
    def _get_next_free_operator(cls, task: Task):
        free_operators = cls._get_free_operators(task)
        if free_operators:
            return random.choice(free_operators)

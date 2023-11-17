import random
from django.db import models
from queue_manager.task.models import Task, Service
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
        QManager.free_operator_appeared(operator=processing_operator)


class QManager:
    @classmethod
    def personal_ticket_appeared(cls, ticket: Ticket, assigned_to: Operator):
        if assigned_to.is_free:
            ticket.assign_to_operator(assigned_to)

    @classmethod
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

    @classmethod
    def _get_next_personal_ticket(cls, operator: Operator) -> Ticket:
        last_status_code = Subquery(Status.objects.filter(
            ticket=OuterRef('id')).order_by('-assigned_at').values(
                'code')[:1])

        last_status_assigned_at = Subquery(Status.objects.filter(
            ticket=OuterRef('id')).order_by('-assigned_at').values(
                'assigned_at')[:1])

        return Ticket.objects.filter(
            status__code=Status.objects.Codes.REDIRECTED,
            status__assigned_to=operator
        ).annotate(last_status_code=last_status_code).filter(
            last_status_code=Status.objects.Codes.REDIRECTED).annotate(
                last_status_assigned_at=last_status_assigned_at).order_by(
            'last_status_assigned_at').first()

    @classmethod
    def _get_next_primary_ticket(
                cls, operator: Operator, primary_task_id=None) -> Ticket:
        '''primary_task is only used to test this method'''

        last_status_code = Subquery(Status.objects.filter(
            ticket=OuterRef('id')).order_by('-assigned_at').values(
                'code')[:1])

        last_status_assigned_at = Subquery(Status.objects.filter(
            ticket=OuterRef('id')).order_by('-assigned_at').values(
                'assigned_at')[:1])

        if primary_task_id is None:
            primary_task_id = Subquery(
                Service.objects.filter(
                    operator=operator,
                    is_servicing=True,
                    priority_for_operator=9
                ).values('task_id')[:1])

        return Ticket.objects.filter(task__id=primary_task_id)\
            .annotate(
                last_status_code=last_status_code,
                last_status_assigned_at=last_status_assigned_at)\
            .filter(last_status_code=Status.objects.Codes.UNASSIGNED)\
            .order_by('last_status_assigned_at').first()

    @classmethod
    def _get_next_secondary_ticket(
            cls, operator: Operator, secondery_tasks_ids=None) -> Ticket:
        '''secondery_tasks_ids is only used to test this method'''

        last_status_code = Subquery(Status.objects.filter(
            ticket=OuterRef('id')).order_by('-assigned_at').values(
                'code')[:1])

        last_status_assigned_at = Subquery(Status.objects.filter(
            ticket=OuterRef('id')).order_by('-assigned_at').values(
                'assigned_at')[:1])

        if secondery_tasks_ids is None:
            secondery_tasks_ids = Subquery(
                Service.objects.filter(
                    operator=operator,
                    is_servicing=True,
                    priority_for_operator__lt=9
                ).values_list('task_id', flat=True))

        return Ticket.objects.filter(task__id__in=secondery_tasks_ids)\
            .annotate(
                last_status_code=last_status_code,
                last_status_assigned_at=last_status_assigned_at)\
            .filter(last_status_code=Status.objects.Codes.UNASSIGNED)\
            .order_by('last_status_assigned_at').first()

    @classmethod
    def _get_free_operators(cls, task: Task):
        '''Returns all operators which:
        - currently is_servicing the task
        - don't currently have ticket in processing'''
        last_assigned_ticket = Subquery(
            Ticket.objects.filter(
                status__assigned_to=OuterRef(OuterRef('id')),
                status__code=Status.objects.Codes.PROCESSING
                ).order_by('-id').values(
                'id')[:1])

        last_status_of_last_ticket = Subquery(Status.objects.filter(
            ticket=last_assigned_ticket).order_by('-assigned_at').values(
                'code')[:1])

        processing_operators = Subquery(
            Operator.objects.filter(id=OuterRef('id')).annotate(
                last_status_of_last_ticket=last_status_of_last_ticket).
            filter(last_status_of_last_ticket=Status.
                   objects.Codes.PROCESSING).values('id'))

        free_operators = task.can_be_served_by.filter(
            service__is_servicing=True).exclude(id__in=processing_operators)
        return free_operators

    @classmethod
    def _get_next_free_operator(cls, task: Task):
        free_operators = cls._get_free_operators(task)
        if free_operators:
            return random.choice(free_operators)

from django.db import models
from django.db.models import Subquery, Q
from django.contrib.auth.models import User
from queue_manager.status.models import Status
from datetime import datetime, timezone

ITEM_NAME = 'session'


class SessionManager(models.Manager):

    class SessionErrors(Exception):
        pass

    class ActiveSessionAlreadyExistsError(SessionErrors):
        '''Raised when attempt is made to create a new active session
        while another active session already exists.'''
        pass

    class NoActiveSessionsError(SessionErrors):
        '''Raised when attempt is made to finish an active session
        while there is no active session'''
        pass

    def _get_last_session_code(self):
        last_session = self\
            .order_by('-started_at')\
            .first()
        if last_session:
            return last_session.code

    def _get_today_date_str(self):
        date_utc = datetime.now(timezone.utc)
        date_local = date_utc.astimezone()
        return date_local.strftime('%Y-%m-%d')

    def _split_code_to_date_and_letter(self, session_code):
        STD_DATE_LENGTH = 10
        if len(session_code) < STD_DATE_LENGTH:
            return '', ''
        date_str = session_code[0: STD_DATE_LENGTH]
        letters = session_code[STD_DATE_LENGTH:]
        return date_str, letters

    def _is_todays_code(self, session_code):
        if session_code:
            date_str, _ = self._split_code_to_date_and_letter(session_code)
            return date_str == self._get_today_date_str()

    def _get_new_session_code(self):
        '''Returns code for new session
        - if there is no todays sessions in db returns "<current date>A"
        - if previous code in db is "<current date>A" returns "<current date>B"
        - if prev. code in db is "<current date>Z" returns "<current date>ZA"
        '''
        last_session_code = self._get_last_session_code()
        if not self._is_todays_code(last_session_code):
            return self._get_today_date_str() + 'A'
        _, last_letters = self._split_code_to_date_and_letter(
                                                    last_session_code)

        if last_letters == '':
            return self._get_today_date_str() + 'A'

        last_char_of_last_letters = last_letters[-1].upper()
        if last_char_of_last_letters == 'Z':
            return self._get_today_date_str() + last_letters + 'A'

        next_char = chr(ord(last_char_of_last_letters) + 1)
        return self._get_today_date_str() + last_letters[:-1] + next_char

    def get_current_session(self):
        '''Returns active session (empty QS if there is no active session)'''
        return self.filter(finished_at__isnull=True)\
            .only('id', 'code').first()

    def subq_current_session_id(self):
        '''Returns subquery with current session id.'''
        return Subquery(
            self
            .filter(finished_at__isnull=True)
            .values('id')[:1])

    def subq_last_session_id(self):
        '''Returns subquery with last session id.'''
        return Subquery(
            self
            .order_by('-started_at')
            .values('id')[:1])

    def start_new_session(self, started_by):
        '''Starts new avtive session (Must be used instead of create()).

        Arguments:
            staarted_by - Supervisor who started this session

        Returns:
            New Session instance (or raise exception)
        '''
        if self.get_current_session():
            raise self.ActiveSessionAlreadyExistsError
        return self.create(
            code=Session.objects._get_new_session_code(),
            started_by=started_by
        )

    def finish_current_session(self, finished_by):
        '''Finishes an active session.

        Arguments:
            finished_by - supervisor who finished this session

        Returns:
            Finished Session instance (or raise exception)
        '''
        current_session = self.get_current_session()
        if not current_session:
            raise self.NoActiveSessionsError
        current_session.finished_by = finished_by
        current_session.finished_at = datetime.now(timezone.utc)
        current_session.save()
        return current_session


class Session(models.Model):
    '''Every day a supervisor starts a new session.
    If there is an active session, clients can print new tickets.
    If a supervisor finished the session, clients can't print no more tickets.
    But issued tickets still can be served by operators.'''
    code = models.CharField(
        max_length=15,
        unique=True,
        verbose_name='Code'
    )
    started_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Started at'
    )
    started_by = models.ForeignKey(
        User,
        related_name='sessions_started_by',
        on_delete=models.PROTECT,
        verbose_name='Started by'
    )
    finished_at = models.DateTimeField(
        null=True,
        verbose_name='Finished at'
    )  # If finished_at is None than the session is Active
    finished_by = models.ForeignKey(
        User,
        related_name='sessions_finished_by',
        null=True,
        on_delete=models.PROTECT,
        verbose_name='Finished by'
    )
    objects = SessionManager()

    class Meta:
        indexes = [
            models.Index(
                fields=['-started_at'],
                include=['id'],
                name='started_at_idx'),
            models.Index(
                fields=['finished_at'],
                include=['id', 'code'],
                condition=Q(finished_at__isnull=True),
                name='finished_at_idx')]

    @property
    def is_active(self):
        '''Is the session active
        (only one active session can exists)'''
        return not bool(self.finished_at)

    @property
    def count_tickets_issued(self):
        '''Returns number of tickets issued during the session'''
        return self.ticket_set.count()

    @property
    def count_tickets_completed(self):
        '''Returns the number of completed tickets in the session'''
        return self.count_tickets_with_last_status_code_in(
            Status.COMPLETED.code)

    @property
    def count_tickets_unprocessed(self):
        '''Returns the number of unprocessed tickets in the session'''
        return self.count_tickets_with_last_status_code_in(
            Status.UNPROCESSED_CODES)

    def count_tickets_with_last_status_code_in(self, last_status_codes):
        '''Returns the number of tickets in the session
        whose last status code is in last_status_codes'''
        from queue_manager.ticket.models import Ticket
        return self.ticket_set\
            .annotate(last_status_code=Ticket.subq_last_status_code())\
            .filter(last_status_code__in=last_status_codes)\
            .count()

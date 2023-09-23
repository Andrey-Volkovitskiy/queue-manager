from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, timezone

ITEM_NAME = 'session'


class SessionManager(models.Manager):
    def _get_last_session_code(self):
        last_session = self.last()
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


class Session(models.Model):
    code = models.CharField(
        max_length=15,
        unique=True,
        verbose_name='Code'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Is active'
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
    )
    finished_by = models.ForeignKey(
        User,
        related_name='sessions_finished_by',
        null=True,
        on_delete=models.PROTECT,
        verbose_name='Finished by'
    )
    objects = SessionManager()

    def save(self, *args, **kwargs):
        if self.code == '':
            self.code = Session.objects._get_new_session_code()
        return super(Session, self).save(*args, **kwargs)

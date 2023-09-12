from django.db import models
from django.core.validators import RegexValidator


only_letters = RegexValidator(
    r'^[a-zA-Z]*$',
    'Only English letters are allowed.')


class CapitalizedCharField(models.CharField):
    def get_prep_value(self, value):
        value = super().get_prep_value(value)
        return value if value is None else value.capitalize()


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

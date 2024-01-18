from queue_manager.user.models import Operator
from queue_manager.task.models import Task, Service
from queue_manager.ticket.models import QManager
from django.contrib.auth.forms import UserCreationForm, SetPasswordForm
from django import forms


class ModelFormWithTaskSet(forms.ModelForm):
    task_set = forms.ModelMultipleChoiceField(
        label="Can serve tasks",
        widget=forms.CheckboxSelectMultiple(),
        queryset=Task.objects.all().order_by('letter_code'),
        required=False)

    def save(self, *args, **kwargs):
        instance = super().save(commit=True)
        instance.task_set.set(self.cleaned_data['task_set'])
        return instance


class OperatorCreateForm(UserCreationForm, ModelFormWithTaskSet):
    class Meta:
        model = Operator
        fields = [
            'first_name',
            'last_name',
            'username',
            'password1',
            'password2',
            'task_set',
            ]


class OperatorUpdateForm(ModelFormWithTaskSet):
    class Meta:
        model = Operator
        fields = [
            'first_name',
            'last_name',
            'username',
            'task_set'
            ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['task_set'].initial = self.instance.task_set.all(
            ).values_list('id', flat=True)


class OperatorChangePasswordForm(SetPasswordForm):
    class Meta:
        model = Operator
        fields = [
            'password1',
            'password2',
            ]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('instance')
        super(SetPasswordForm, self).__init__(*args, **kwargs)


class OperatorStartServiceForm(forms.ModelForm):
    '''Operator selects prim. and secondary tasks that will be served.'''
    class Meta:
        model = Operator
        fields = [
            'primary_task',
            'secondary_tasks',
            ]

    primary_task = forms.ModelChoiceField(
        label="Primary task",
        queryset=None,
        required=True)

    secondary_tasks = forms.ModelMultipleChoiceField(
        widget=forms.CheckboxSelectMultiple(),
        label="Secondary tasks",
        queryset=None,
        required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        available_tasks = self.instance.task_set\
            .all().order_by('letter_code')
        self.fields['primary_task'].queryset = available_tasks
        self.fields['secondary_tasks'].queryset = available_tasks

    def save(self, *args, **kwargs):
        instance = super().save(*args, **kwargs)

        primary_service = instance.service_set.get(
                task=self.cleaned_data['primary_task'])
        primary_service.priority = Service.HIGHEST_PRIORITY
        primary_service.save()

        secondary_tasks_cleaned = self.cleaned_data['secondary_tasks'].exclude(
                    id=self.cleaned_data['primary_task'].id)
        secondary_services = instance.service_set.filter(
                    task__in=secondary_tasks_cleaned)
        secondary_services.update(
            priority=Service.LOWEST_PRIORITY
        )

        if not instance.current_ticket:
            QManager.free_operator_appeared(operator=instance)

        return instance

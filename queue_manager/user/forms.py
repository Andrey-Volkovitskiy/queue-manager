from queue_manager.user.models import Operator
from queue_manager.task.models import Task
from django.contrib.auth.forms import UserCreationForm, SetPasswordForm
from django import forms


class OperatorCreateForm(UserCreationForm):
    class Meta:
        model = Operator
        fields = [
            'first_name',
            'last_name',
            'username',
            'password1',
            'password2',
            ]


class OperatorUpdateForm(forms.ModelForm):
    class Meta:
        model = Operator
        fields = [
            'username',
            'first_name',
            'last_name',
            'task_set'
            ]

    task_set = forms.ModelMultipleChoiceField(
        label="Can serve tasks",
        widget=forms.CheckboxSelectMultiple(),
        queryset=Task.objects.all().order_by('letter_code'),
        required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['task_set'].initial = self.instance.task_set.all(
            ).values_list('id', flat=True)

    def save(self, *args, **kwargs):
        instance = super().save(*args, **kwargs)
        instance.task_set.set(self.cleaned_data['task_set'])
        return instance


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

from queue_manager.user.models import Operator
from django.contrib.auth.forms import UserCreationForm, SetPasswordForm
from django.forms import ModelForm


class OperatorCreateForm(UserCreationForm):
    class Meta:
        model = Operator
        fields = [
            'username',
            'password1',
            'password2',
            'first_name',
            'last_name',
            ]


class OperatorUpdateForm(ModelForm):
    class Meta:
        model = Operator
        fields = [
            'username',
            'first_name',
            'last_name',
            ]


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

from queue_manager.user.models import Operator
from django import forms


class OperatorForm(forms.ModelForm):
    class Meta:
        model = Operator
        fields = [
            'username',
            'password',
            'first_name',
            'last_name',
            ]

from queue_manager.user.models import Operator
from django.contrib.auth.forms import UserCreationForm


class OperatorForm(UserCreationForm):
    class Meta:
        model = Operator
        fields = [
            'username',
            'password1',
            'password2',
            'first_name',
            'last_name',
            ]

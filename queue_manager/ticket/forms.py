from queue_manager.user.models import Operator
from queue_manager.ticket.models import Ticket
from django import forms


class TicketRedirectForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = [
            'redirect_to',
            ]

    redirect_to = forms.ModelChoiceField(
        label="To following (serving) operator:",
        queryset=Operator.objects.none()
    )

    def __init__(self, *args, **kwargs):
        redirected_by = kwargs.pop('redirected_by', None)
        super().__init__(*args, **kwargs)
        if redirected_by:
            all_serving_operators = Operator.objects.filter(
                service__is_servicing=True).distinct().order_by(
                    'first_name', 'last_name')
            operators_except_request_user = all_serving_operators.exclude(
                id=redirected_by)
            self.fields['redirect_to'].queryset = operators_except_request_user

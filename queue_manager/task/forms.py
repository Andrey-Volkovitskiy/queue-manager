from queue_manager.task.models import Task
from django import forms


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = [
            'letter_code',
            'name',
            'description',
            'can_be_served_by',
        ]
        widgets = {
            'can_be_served_by': forms.CheckboxSelectMultiple
        }

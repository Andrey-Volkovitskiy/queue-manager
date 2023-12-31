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

    def clean_letter_code(self):
        data = self.cleaned_data['letter_code']
        if self.Meta.model.objects.filter(letter_code=data).exists():
            raise forms.ValidationError(
                f'The letter code "{data}" already exists')
        return data

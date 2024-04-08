from django.utils import timezone
from django import forms

from .models import Task, Tag
from accounts.models import User


class TaskForm(forms.ModelForm):
    tags = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'tag-input'}))

    class Meta:
        model = Task
        fields = ['title', 'description', 'deadline', 'assignees', 'tags']
        widgets = {
            'deadline': forms.DateInput(attrs={'type': 'date'}),
            'assignees': forms.SelectMultiple(attrs={'class': 'assignees-input'})
        }

    def clean_deadline(self):
        deadline = self.cleaned_data.get('deadline')
        if deadline and deadline < timezone.now().date():
            raise forms.ValidationError("Дедлайн не може бути раніше сьогоднішньої дати.")
        return deadline

    def clean(self):
        cleaned_data = super().clean()
        title = cleaned_data.get('title')
        deadline = cleaned_data.get('deadline')
        assignees = cleaned_data.get('assignees')

        # Перевірка обов'язкових полів
        if not title:
            self.add_error('title', 'Це поле є обов\'язковим.')
        if not deadline:
            self.add_error('deadline', 'Це поле є обов\'язковим.')
        if not assignees:
            self.add_error('assignees', 'Це поле є обов\'язковим.')
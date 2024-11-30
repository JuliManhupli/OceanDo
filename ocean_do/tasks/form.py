from django.utils import timezone
from django import forms

from .models import Task, ChatComment


class TaskForm(forms.ModelForm):
    tags = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'tag-input'}))

    class Meta:
        model = Task
        fields = ['title', 'description', 'deadline', 'tags']
        widgets = {
            'deadline': forms.DateInput(attrs={'type': 'date'}),
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

        # Перевірка обов'язкових полів
        if not title:
            self.add_error('title', 'Це поле є обов\'язковим.')
        if not deadline:
            self.add_error('deadline', 'Це поле є обов\'язковим.')


class TaskEditForm(forms.ModelForm):
    tags = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'tag-input'}))

    class Meta:
        model = Task
        fields = ['title', 'description', 'deadline', 'tags']
        widgets = {
            'deadline': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        title = cleaned_data.get('title')
        deadline = cleaned_data.get('deadline')

        # Перевірка обов'язкових полів
        if not title:
            self.add_error('title', 'Це поле є обов\'язковим.')
        if not deadline:
            self.add_error('deadline', 'Це поле є обов\'язковим.')


class CommentForm(forms.ModelForm):
    class Meta:
        model = ChatComment
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={'class': 'comment-text-to-send', 'placeholder': 'Введіть текст...'}),
        }

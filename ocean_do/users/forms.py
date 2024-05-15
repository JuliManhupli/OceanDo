from accounts.models import Group
from django import forms
from django.core.exceptions import ValidationError


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name']

    def clean(self):
        cleaned_data = super().clean()
        title = cleaned_data.get('name')

        # Перевірка обов'язкових полів
        if not title:
            self.add_error('name', 'Це поле є обов\'язковим.')


class UserUpdateForm(forms.Form):
    file = forms.FileField(required=False)
    username = forms.CharField(required=False, widget=forms.TextInput(attrs={"class": "data-input"}))
    role = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={"class": "data-input"}))

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            max_size = 2 * 1024 * 1024
            if file.size > max_size:
                raise ValidationError('Розмір файлу не повинен перевищувати 2 МБ.')

            allowed_extensions = ['jpg', 'jpeg', 'png']
            file_extension = file.name.split('.')[-1].lower()
            if file_extension not in allowed_extensions:
                raise ValidationError('Файл повинен бути зображенням у форматі JPG, JPEG або PNG.')
        return file

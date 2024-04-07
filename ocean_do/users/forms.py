from django.core.exceptions import ValidationError
from django.forms import Form, FileField, CharField, TextInput


class UserUpdateForm(Form):
    file = FileField(required=False)
    username = CharField(required=False, widget=TextInput(attrs={"class": "data-input"}))

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            max_size = 2 * 1024 * 1024
            if file.size > max_size:
                raise ValidationError('Розмір файлу не повинен перевищувати 2 МБ.')
        return file
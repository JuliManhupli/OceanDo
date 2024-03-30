from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
from django.forms import PasswordInput, CharField, EmailField, TextInput, EmailInput, Form
from .models import User


class RegisterForm(UserCreationForm):
    username = CharField(max_length=16, min_length=3, required=True, widget=TextInput(attrs={"class": "data-input"}))
    email = EmailField(max_length=100, required=True, widget=EmailInput(attrs={"class": "data-input"}))
    password1 = CharField(required=True, widget=PasswordInput(attrs={"class": "data-input"}))
    password2 = CharField(required=True, widget=PasswordInput(attrs={"class": "data-input"}))

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email').lower()
        if User.objects.filter(email=email).exists():
            raise ValidationError("Така електронна пошта вже використовується!")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not username:
            raise ValidationError("Це поле є обов'язковим.")
        return username

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        username = self.cleaned_data.get("username")

        if len(password1) < 8:
            raise ValidationError("Цей пароль занадто короткий. Він повинен містити щонайменше 8 символів!")
        if password1.isdigit():
            raise ValidationError("Цей пароль повинен містити хоча б один символ, який не є цифрою!")
        if username.lower() in password1.lower():
            raise ValidationError("Пароль занадто схожий на ім'я користувача!")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Паролі не співпадають!")
        return password2


class LoginForm(AuthenticationForm):
    email = EmailField(max_length=100, required=True, widget=EmailInput(attrs={"class": "data-input"}))
    password = CharField(required=True, widget=PasswordInput(attrs={"class": "data-input"}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].required = False

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        if email and password:
            self.user_cache = authenticate(email=email, password=password)
            if self.user_cache is None:
                raise ValidationError('Неправильна електронна пошта або пароль.')

        return self.cleaned_data

    def get_user(self):
        return self.user_cache


class ChangePasswordForm(Form):
    new_password = CharField(label='Новий пароль', widget=PasswordInput(attrs={"class": "data-input"}))
    confirm_new_password = CharField(label='Підтвердіть новий пароль', widget=PasswordInput(attrs={"class": "data-input"}))
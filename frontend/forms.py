from django import forms
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.hashers import check_password
from django.contrib.auth.password_validation import validate_password
from django.db import models

User = get_user_model()


class UserLoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    """ Проверка на валидацию"""

    def clean(self, *args, **kwargs):
        email = self.cleaned_data.get('email').strip()
        password = self.cleaned_data.get('password').strip()

        if email and password:
            qs = User.objects.filter(email=email)
            if not qs.exists():
                raise forms.ValidationError('Такого пользователя нет!')
            if not check_password(password, qs[0].password):
                raise forms.ValidationError('Пароль не верный!')

            # проверяем существует ли пользователь
            user = authenticate(email=email, password=password)

            if not user:
                raise forms.ValidationError('Данный аккаунт отключен')

        return self.cleaned_data


class UserCreateForm(forms.Form):
    email = forms.EmailField(
        label='Введите email',
        required=False,
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "required": True
            }
        )
    )

    username = forms.CharField(
        label='Введите username',
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "required": True
            }
        )
    )

    password = forms.CharField(
        label='Введите пароль',
        validators=[validate_password],
        required=False,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "required": True
            }
        )
    )


class UpdatePostForm(forms.Form):
    class ParseModeChoices(models.TextChoices):
        DEFAULT = "DEFAULT"
        MARKDOWN = "MARKDOWN"
        HTML = "HTML"
        DISABLED = "DISABLED"

    title = forms.CharField(
        label='Заголовок',
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "required": True
            }
        )
    )

    description = forms.CharField(
        label='Описание',
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "required": True
            }
        )
    )

    hash_tag = forms.CharField(
        label='Хэш-теги',
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "required": True
            }
        )
    )

    parse_mode = forms.ChoiceField(
        choices=ParseModeChoices.choices,
        label='Тип текста',
        required=False,
        widget=forms.Select(
            attrs={
                "class": "form-control",
                "required": True
            }
        )
    )


# class CreatePostForm(forms.ModelForm):
#     class Meta:
#         model = Post
#         fields = [
#             'title',
#             'description',
#             'hash_tag',
#             'parse_mode',
#             'photo',
#             'video',
#             'chats'
#         ]

class CreatePostForm(UpdatePostForm):
    def __init__(self, *args, **kwargs):
        chats = kwargs.pop('chats')
        super().__init__(*args, **kwargs)
        self.fields['chats'].choices = chats

    photo = forms.ImageField(
        label='Фото',
        required=False,
        widget=forms.ClearableFileInput(
            attrs={
                "class": "form-control",
            }
        )
    )

    video = forms.FileField(
        label='Фото',
        required=False,
        widget=forms.ClearableFileInput(
            attrs={
                "class": "form-control",
            }
        )
    )

    chats = forms.MultipleChoiceField(
        label='Чаты',
        required=False,
        widget=forms.SelectMultiple(
            attrs={
                "class": "form-control",
                "required": True
            }
        )
    )

    def clean(self):
        if not self.files:
            raise forms.ValidationError("Укажите поле фото или видео")

        return self.cleaned_data

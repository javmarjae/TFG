from pyexpat import model
from statistics import mode
from urllib import request
from attr import attrs
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, SetPasswordForm, PasswordResetForm
from django.contrib.auth import get_user_model
from pkg_resources import require

from web.models import Gamer, Gameship, Game

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(help_text='A valid email address, please.', required=True)

    LANGUAGES = (
        ('EN','English'),
        ('SP','Spanish'),
        ('FR','French'),
        ('GE','German'),
        ('CH','Chinese')
    )

    language = forms.ChoiceField(choices=LANGUAGES, help_text="Choose your language.")
    birth_date = forms.DateField(required=True, help_text="Birth date")

    class Meta:
        model = get_user_model()
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2','language','birth_date']

    def save(self, commit=True):
        user = super(UserRegisterForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        user.language = self.cleaned_data['language']
        user.birth_date = self.cleaned_data['birth_date']
        if commit:
            user.save()
        return user

class UserLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(UserLoginForm, self).__init__(*args, **kwargs)

    username = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Username or Email'}),
        label="Username or Email")

    password = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': 'Password'}))

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = get_user_model()
        fields = ['first_name', 'last_name', 'email','profile_pic','username','is_online']

class GamerUpdateForm(forms.ModelForm):
    class Meta:
        model = Gamer
        fields = ['user','discord', 'steam', 'epic_games','riot_games']

class GameshipUpdateForm(forms.ModelForm):
    game = forms.ModelChoiceField(queryset=Game.objects.all(), widget=forms.Select(attrs={
        'class': 'form-control select2'
    }))

    rank = forms.ChoiceField(choices=Gameship.GAMES_RANKS, widget=forms.Select(attrs={
        'class': 'form-control select2'
    }))

    class Meta:
        model = Gameship
        fields = ['rank','game','gamer']

class SetPasswordForm(SetPasswordForm):
    class Meta:
        model = get_user_model()
        fields = ['new_password1', 'new_password2']

class PasswordResetForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super(PasswordResetForm, self).__init__(*args, **kwargs)
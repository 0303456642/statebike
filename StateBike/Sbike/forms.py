from django import forms
from django.contrib.auth.models import User
from .models import Client

class ClientRegisterForm(forms.Form):
    username = forms.CharField(min_length=6, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password1 = forms.CharField(min_length=8, widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))
    password2 = forms.CharField(min_length=8, widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'}))

    first_name = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}))
    email = forms.EmailField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'example@example.com'}))

    phone_number = forms.IntegerField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional'}))
    dni = forms.IntegerField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'DNI'}))
    card_number = forms.IntegerField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Card Number'}))
    expiration_date = forms.DateField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'YYYY-MM-DD'}))
    security_code = forms.IntegerField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'xxxx'}))

    def clean_username(self):
        """Comprueba que no existe el mismo user en la db"""
        username = self.cleaned_data['username']
        if User.objects.filter(username=username):
            raise forms.ValidationError('Ya existe ese nombre de usuario')
        return username

    def clean_email(self):
        """Comprueba que no existe el mismo email en la db"""
        email = self.cleaned_data['email']
        if User.objects.filter(email=email):
            raise forms.ValidationError('Ya se ha registrado ese email')
        return email

    def clean_password2(self):
        """Comprueba que ambas passwords sean iguales"""
        password1 = self.cleaned_data['password1']
        password2 = self.cleaned_data['password2']
        if password1 != password2:
            raise forms.ValidationError('Las passwords no coinciden')
        return password2

    def clean_dni(self):
        """Comprueba que no existe el mismo dni en la db"""
        dni = self.cleaned_data['dni']
        if Client.objects.filter(dni=dni):
            raise forms.ValidationError('Ya se ha registrado ese dni')
        return dni

class ClientEditPasswordForm(forms.Form):
    password1 = forms.CharField(min_length=8, widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))
    password2 = forms.CharField(min_length=8, widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'}))

    def clean_password2(self):
        """Comprueba que ambas passwords sean iguales"""
        password1 = self.cleaned_data['password1']
        password2 = self.cleaned_data['password2']
        if password1 != password2:
            raise forms.ValidationError('Las passwords no coinciden')
        return password2

class ClientEditForm(forms.Form):
    email = forms.EmailField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'example@example.com'}))
    phone_number = forms.IntegerField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional'}))
    card_number = forms.IntegerField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Card Number'}))
    expiration_date = forms.DateField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'YYYY-MM-DD'}))
    security_code = forms.IntegerField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'xxxx'}))

    def clean_email(self):
        """Comprueba que no existe el mismo email en la db"""
        """si el email esta vacio no comprueba nada"""
        email = self.cleaned_data['email']
        if User.objects.filter(email=email):
            raise forms.ValidationError('Ya se ha registrado ese email')
        return email

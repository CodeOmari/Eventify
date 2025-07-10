from django import forms
from django.forms import Widget
from django.contrib.auth import password_validation
from django.utils.translation import gettext_lazy as _

from main_app.models import Events, Registration


class EventForm(forms.ModelForm):
    class Meta:
        model = Events
        fields = ['organizer', 'event_name', 'event_description', 'event_date', 'event_time',
                  'event_location', 'event_price', 'event_image']
        widgets = {
            'event_date': forms.DateInput(attrs={'type': 'date', 'min':'2024-12-05'}),
            'event_price': forms.NumberInput(attrs={'type': 'number'}),
        }

class RegistrationForm(forms.ModelForm):
    class Meta:
        model = Registration
        fields = ['first_name', 'last_name', 'phone_number', 'event_name', 'amount']

class LoginForm(forms.Form):
    username = forms.CharField(max_length=50)
    password = forms.CharField(widget=forms.PasswordInput)


class PasswordChangeForm(forms.Form):
    error_messages = {
        'password_mismatch': _("The two password fields didn’t match."),
    }

    old_password = forms.CharField(
        label=_("Old password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password', 'autofocus': True}),
    )
    new_password1 = forms.CharField(
        label=_("New password"),
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        strip=False,
        help_text=password_validation.password_validators_help_text_html(),
    )
    new_password2 = forms.CharField(
        label=_("New password confirmation"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_old_password(self):
        old_password = self.cleaned_data.get("old_password")
        if not self.user.check_password(old_password):
            raise forms.ValidationError(
                _("Your old password was entered incorrectly. Please enter it again."),
                code='invalid',
            )
        return old_password

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("new_password1")
        password2 = cleaned_data.get("new_password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        return cleaned_data

    def save(self, commit=True):
        password = self.cleaned_data["new_password1"]
        self.user.set_password(password)
        if commit:
            self.user.save()
        return self.user


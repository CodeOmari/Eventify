from django import forms
from django.forms import Widget

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


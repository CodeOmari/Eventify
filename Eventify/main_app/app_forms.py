from django import forms
from django.forms import Widget

from main_app.models import Event


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['organizer', 'event_type','event_name', 'event_description', 'event_date', 'start_time',
                  'end_time','event_location', 'event_slots', 'event_price', 'is_free', 'event_image']
        labels = {
            'organizer': 'Event Organizer',
            'event_type': 'Event Type',
            'event_name': 'Event Name',
            'event_description': 'Event Description',
            'event_date': 'Date',
            'start_time': 'Start Time',
            'end_time': 'End Time',
            'event_location': 'Location',
            'event_slots': 'Event Slots',
            'event_price': 'Price (Ksh)',
            'is_free': 'Free Entry',
            'event_image': 'Event Image',
        }
        widgets = {
            'event_date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        price = cleaned_data.get('event_price')
        is_free = cleaned_data.get('is_free')

        if is_free and price:
            raise forms.ValidationError("Free events should not have a price.")

        if not is_free and not price:
            raise forms.ValidationError("Please enter a price or mark as free.")

        return cleaned_data


class LoginForm(forms.Form):
    username = forms.CharField(max_length=50)
    password = forms.CharField(widget=forms.PasswordInput)


class PasswordResetForm(forms.Form):
    new_password = forms.CharField(label='New Password', widget=forms.PasswordInput(attrs={'placeholder': 'Enter new password'}))
    confirm_password = forms.CharField(label='Confirm Password', widget=forms.PasswordInput(attrs={'placeholder': 'Confirm new password'}))

    def clean(self):
        cleaned_data= super().clean()
        password1 = cleaned_data.get("new_password")
        password2 = cleaned_data.get("confirm_password")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return cleaned_data
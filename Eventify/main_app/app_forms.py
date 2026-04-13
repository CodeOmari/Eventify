from django import forms
from django.forms import Widget

from main_app.models import Event, Ticket

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email
    

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
            'event_price': 'Price (Leave empty if event is free)',
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
    

class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['full_name', 'email', 'phone_number', 'tickets']

    labels = {
        'full_name': 'Enter your full name',
        'email': 'Email Address',
        'phone_number': 'Phone Number e.g 0712345678',
        'tickets': 'Number of Tickets',
    }


class LoginForm(forms.Form):
    username = forms.CharField(max_length=50)
    password = forms.CharField(widget=forms.PasswordInput)


class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(label='Enter your email address')


class SetNewPasswordForm(forms.Form):
    new_password = forms.CharField(label='New Password',
                                   widget=forms.PasswordInput(attrs={'placeholder': 'Enter new password'}))
    confirm_password = forms.CharField(label='Confirm Password',
                                       widget=forms.PasswordInput(attrs={'placeholder': 'Confirm new password'}))

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("new_password")
        password2 = cleaned_data.get("confirm_password")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return cleaned_data
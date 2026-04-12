from django.shortcuts import render, redirect, get_object_or_404

from django.utils.timezone import now
from datetime import timedelta
from main_app.models import Event

from main_app.app_forms import EventForm, LoginForm
from django.contrib import messages

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required

# Create your views here.
def events(request):
    today = now()
    five_days_later = today + timedelta(days=5)
    upcoming_events = Event.objects.filter(event_date__range=(today, five_days_later)).order_by('event_date')

    data = Event.objects.all()

    event_type = request.GET.get('type')

    if event_type:
        events = Event.objects.filter(event_type=event_type)
    else:
        events = Event.objects.all()

    context = {
        'upcoming_events': upcoming_events,
        'data': data,
        'events': events,
    }
    return render(request, 'events.html', context)


@login_required
def create_event(request):
    if request.method == "POST":
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, f"Event {form.cleaned_data['event_name']} was added successfully!")
            return redirect('events')
    else:
        form = EventForm()
    return render(request, 'create_event.html', {"form": form})


def login_user(request):
    if request.method == "GET":
        form = LoginForm()
        return render(request, "login_form.html", {"form": form})
    elif request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                return redirect('events')
        messages.error(request, "Invalid username or password")
        return render(request, "login_form.html", {"form": form})
    

@login_required
def signout_user(request):
    logout(request)
    return redirect('login')


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account creation for {username} was successful!')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'register_form.html', {'form': form})

def event_details(request, id):
    event = get_object_or_404(Event, id=id)
    return render(request, 'event_details.html', {'event': event})
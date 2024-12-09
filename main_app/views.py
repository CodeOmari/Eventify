from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Q
from django.shortcuts import render, redirect
from django.utils.timezone import now

from main_app.app_forms import EventForm, LoginForm, TicketForm
from main_app.models import Events


# Create your views here.

@login_required
def dashboard(request):
    today = now()
    five_days_later = today + timedelta(days=5)
    upcoming_events = Events.objects.filter(event_date__range=(today, five_days_later)).order_by('event_date')

    # Pass data to the template
    context = {
        'username': request.user.username,
        'upcoming_events': upcoming_events,
    }
    return render(request, 'Dashboard.html', context)


@login_required
def about(request):
    return render(request, 'about.html')


@login_required
def events(request):
    data = Events.objects.all()
    return render(request, 'events.html', {"data": data})


@login_required
@permission_required("main_app.add_event", raise_exception=True)
def add_event(request):
    if request.method == "POST":
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, f"Event {form.cleaned_data['event_name']} was added successfully!")
            return redirect('events')
    else:
        form = EventForm()
    return render(request, 'add_event.html', {"form": form})


@login_required
def search_event(request):
    search_term = request.GET.get('search')
    data= Events.objects.filter(Q(event_name__icontains=search_term) | Q(organizer__icontains=search_term)
                                 | Q(event_location__icontains=search_term))
    return render(request, 'event_opener.html', {"data": data, "search_term": search_term})


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
                return redirect('dashboard')
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
    return render(request, 'register.html', {'form': form})


def get_ticket(request):
    if request.method == "POST":
        form = TicketForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('events')
    else:
        form = TicketForm()
    return render(request, 'get_ticket.html', {"form": form})
import json
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt
from django_daraja.mpesa.core import MpesaClient


from main_app.app_forms import EventForm, LoginForm, RegistrationForm, PasswordResetForm
from main_app.models import Events, Registration, Payments


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


def update_password(request, username):
    user = get_object_or_404(User, username=username)

    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            user_password = form.cleaned_data["new_password"]
            user.password = make_password(user_password)
            user.save()
            messages.success(request, 'Password updated successfully!')
            return redirect('login')
    else:
        form = PasswordResetForm()
    return render(request, "password_reset.html", {'form': form, 'username': username})






def register_event(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, f"Registration for {form.cleaned_data['event_name']} was  successful!")
            return redirect('payment_page')
    else:
        form = RegistrationForm()
    return render(request, 'registration_form.html', {"form": form})


def payment_page(request):
    registration = Registration.objects.last()
    return render(request, 'payment_page.html', {'registration': registration})


def payment(request, id):
    registration = get_object_or_404(Registration, pk=id)
    phone_number = registration.phone_number

    cl = MpesaClient()
    phone_number = registration.phone_number
    amount = registration.amount
    account_reference = "Eventify Ticket"
    transaction_desc = 'sacco payments'
    callback_url = 'https://flying-regularly-honeybee.ngrok-free.app/callback'
    response = cl.stk_push(phone_number, amount, account_reference, transaction_desc, callback_url)
    if response.response_code == "0":
        payment = Payments.objects.create(registration=registration,
                                          merchant_request_id=response.merchant_request_id,
                                          checkout_request_id=response.checkout_request_id)
        payment.save()
        messages.success(request, f"Your payment was initiated successfully!")
    return redirect('dashboard')


def callback(request):
    repo = json.loads(request.body)
    data = repo.get['Body']['stkCallback']
    if data["ResultCode"] == "0":
        m_id = ["MerchantRequestID"]
        c_id = ["CheckoutRequestID"]
        code = ""
        item = data["CallbackMetadata"]["Item"]
        for i in item:
            name = i["Name"]
            if name == "MpesaReceiptNumber":
                code = i["Value"]
        registration = Registration.objects.get(merchant_request_id=m_id, checkout_request_id=c_id)
        registration.code = code
        registration.status = "COMPLETED"
        registration.save()
    return HttpResponse("OK")

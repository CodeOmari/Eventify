from django.shortcuts import render, redirect, get_object_or_404

from django.utils import timezone
from django.utils.timezone import now
from datetime import timedelta
from main_app.models import Event

from main_app.app_forms import CustomUserCreationForm, EventForm, LoginForm, TicketForm, PasswordResetRequestForm, SetNewPasswordForm
from django.contrib import messages

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required

from django.core.mail import EmailMultiAlternatives
from django.conf import settings

from django.db.models import Q

from django.contrib.auth.models import User
from django.urls import reverse
from django.core.signing import TimestampSigner, SignatureExpired, BadSignature
from django.contrib.auth.hashers import make_password

signer = TimestampSigner()

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
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account creation for {username} was successful!')
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register_form.html', {'form': form})


def event_details(request, id):
    event = get_object_or_404(Event, id=id)
    return render(request, 'event_details.html', {'event': event})

def search_event(request):
    search_term = request.GET.get('search')
    data= Event.objects.filter(Q(event_name__icontains=search_term) | Q(organizer__icontains=search_term)
                                 | Q(event_location__icontains=search_term) | Q(event_type__icontains=search_term))
    return render(request, 'event_opener.html', {"data": data, "search_term": search_term})


@login_required
def get_ticket(request, id):
    event = get_object_or_404(Event, id=id)
    
    if request.method == "POST":
        form = TicketForm(request.POST, request.FILES)
    

        if event.booked_slots  >= event.event_slots:
                messages.error(request, "This event is fully booked.")
                return redirect("events")
        
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.event = event
            ticket.save()

            event.booked_slots += ticket.tickets
            event.save()

            html_content = f"""
                <div>
                    <h2 style='color: #3542D4; text-align: center;'> Eventify </h2>

                    <p> Hi <strong>{ticket.full_name}</strong>, </p>

                    <p>
                         You have successfully booked a ticket. Find event details attached below:
                    </p>

                    <h3>Event Details</h3>

                    <ul>
                        <li><strong> Ticket ID: </strong> 
                            #{ticket.id}
                        </li>
                        <li><strong> Number of Ticket(s): </strong> 
                            {ticket.tickets}
                        </li>
                        <li><strong> Event: </strong> 
                            {event.event_name}
                        </li>
                        <li><strong> Location: </strong>
                            {event.event_location}
                        </li>
                        <li><strong>  Date & Time: </strong>
                            {event.event_date} &middot; {event.start_time.strftime("%I:%M %p")}
                        </li>
                        <li><strong> Price: </strong> 
                            { "Free" if event.is_free == True else f'Ksh {event.event_price} per ticket' }
                        </li>
                    </ul>

                    <p>
                        Please present this email at the event entrance. If your ticket has a fee,
                        payment shall be done at the entrance.
                    </p>

                    <hr>

                    <p>
                        &copy; {timezone.now().year} Eventify. All rights reserved.
                    </p>
                </div>
            """

            subject = "Your Event Ticket"
            from_email = settings.DEFAULT_FROM_EMAIL
            to = [ticket.email]

            message = EmailMultiAlternatives(subject, "", from_email, to)
            message.attach_alternative(html_content, "text/html")
            message.send()

            messages.success(request, "Ticket booked successfully! A confirmation email has been sent to your email.")
            return redirect("events")
    else:
        form = TicketForm()
    return render(request, 'ticket_form.html', {"form":form, "event":event})



def password_reset_request(request):
    if request.method == "POST":
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
                token = signer.sign(user.pk) # sign user id
                reset_link = request.build_absolute_uri(
                    reverse('password_reset_confirm', args=[token])
                )

                html_content = f"""
                    <div>
                        <h2 style='color: #3542D4; text-align: center;'> Eventify </h2>

                        <p> Hi <strong>{user.username}</strong>, </p>

                        <p>
                            You requested a password reset. Click the link below to set a new password:
                        </p>

                        <p style='margin: 20px 0;'>
                            <a href="{reset_link}" style='display: inline-block; 
                                                   padding: 10px 15px; background-color: #004f71; color: white; 
                                                   text-decoration: none; border-radius: 5px;'>
                                Reset Password
                            </a>
                        </p>

                        <p>
                            If the above button doesn't work, copy and paste the following link into your browser:
                        </p>

                        <p>
                            <a href="{reset_link}">{reset_link}</a>
                        </p>

                        <p>
                            The link is valid for 30 minutes only.
                        </p>

                        <hr>

                        <p>
                            If you did not request a password reset, please ignore this email. <br>
                            &copy; {timezone.now().year} NovaCare. All rights reserved.
                        </p>
                    </div>
                """

                subject = "Password Reset Request"
                from_email = settings.DEFAULT_FROM_EMAIL
                to = [email]

                message = EmailMultiAlternatives(subject, "", from_email, to)
                message.attach_alternative(html_content, "text/html")
                message.send()


                messages.success(request, f'Your password reset link has been sent to {email}.')
                return redirect('login')
            except User.DoesNotExist:
                messages.error(request, f'No user found with the email {email}.')
    else:
        form = PasswordResetRequestForm()
    return render(request, "password_reset.html", {'form': form})


def password_reset_confirm(request, token):
    try:
        user_id = signer.unsign(token, max_age=3600) # token id valid for 1 hour
        user = User.objects.get(pk=user_id)
    except (BadSignature, SignatureExpired, User.DoesNotExist):
        messages.error(request, 'Invalid or expired reset link.')
        return redirect("user_management:password_reset_request")

    if request.method == "POST":
        form = SetNewPasswordForm(request.POST)
        if form.is_valid():
            user_password = form.cleaned_data["new_password"]
            user.password = make_password(user_password)
            user.save()
            messages.success(request, 'Password updated successfully!')
            return redirect('login')
    else:
        form = SetNewPasswordForm()
    return render(request, 'password_reset_confirm.html', {'form': form})
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from django.utils import timezone
from main_app.models import Event, Ticket

from main_app.app_forms import CustomUserCreationForm, EventForm, LoginForm, TicketForm, PasswordResetRequestForm, SetNewPasswordForm
from django.contrib import messages

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required

from django.core.mail import EmailMultiAlternatives
from django.conf import settings

from django.db.models import Q

from django.contrib.auth.models import User
from django.urls import reverse
from django.core.signing import TimestampSigner, SignatureExpired, BadSignature
from django.contrib.auth.hashers import make_password

from django.core.paginator import Paginator
from django.db import IntegrityError, transaction

signer = TimestampSigner()

# Create your views here.
def events(request):
    current_datetime = timezone.localtime()
    today = current_datetime.date()
    current_time = current_datetime.time().replace(tzinfo=None)

    happening_today = Event.objects.filter(
        event_date=today,
        end_time__gt=current_time
    ).order_by('start_time')

    all_events = Event.objects.filter(
        event_date__gt=today
    ).order_by('event_date', 'start_time')

    # Get selected event category
    event_type = request.GET.get('type', '').upper()

    # Validate and filter by category
    valid_types = [choice[0] for choice in Event.EVENT_TYPES]

    if event_type in valid_types:
        happening_today = happening_today.filter(
            event_type=event_type
        )

        all_events = all_events.filter(
            event_type=event_type
        )

    context = {
        'happening_today': happening_today,
        'upcoming_events': happening_today,
        'all_events': all_events,
        'events': all_events,
        'data': all_events,
        'year': today.year,
        'selected_type': event_type.lower(),
    }

    return render(request, 'events.html', context)

@login_required
def create_event(request):
    if request.method == "POST":
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user
            event.save()
            messages.success(request, f"Event {form.cleaned_data['event_name']} was added successfully!")
            return redirect('dashboard')
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

def event_details(request, slug):
    event = get_object_or_404(Event, slug=slug)
    return render(request, 'event_details.html', {'event': event})

def search_event(request):
    current_datetime = timezone.localtime()
    today = current_datetime.date()
    current_time = current_datetime.time()

    search_term = request.GET.get('search', '').strip()

    upcoming_events = Event.objects.filter(
        Q(event_date__gt=today) |
        Q(event_date=today, end_time__gt=current_time)
    )

    data = upcoming_events.filter(
        Q(event_name__icontains=search_term) |
        Q(organizer__icontains=search_term) |
        Q(event_location__icontains=search_term) |
        Q(event_type__icontains=search_term)
    ).order_by('event_date', 'start_time')

    return render(
        request,
        'event_opener.html',
        {
            'data': data,
            'search_term': search_term,
        }
    )



def get_ticket(request, slug):
    event = get_object_or_404(Event, slug=slug)

    if request.method == "POST":
        form = TicketForm(request.POST, request.FILES)

        if form.is_valid():

            ticket = form.save(commit=False)
            ticket.event = event

            # Check for an existing booking using the same phone number
            existing_ticket = Ticket.objects.filter(
                event=event,
                phone_number=ticket.phone_number
            ).exists()

            if existing_ticket:
                messages.warning(
                    request,
                    "You have already booked a ticket for this event using this phone number."
                )
                return redirect("events")

            # Check whether the event is fully booked
            if event.booked_slots >= event.event_slots:
                messages.error(
                    request,
                    "This event is fully booked."
                )
                return redirect("events")

            # Check whether the requested tickets exceed available slots
            if event.booked_slots + ticket.tickets > event.event_slots:
                messages.error(
                    request,
                    f"Only {event.event_slots - event.booked_slots} "
                    "ticket(s) remaining for this event."
                )
                return redirect("events")

            # Save ticket and update event capacity safely
            try:
                with transaction.atomic():
                    ticket.save()

                    event.booked_slots += ticket.tickets
                    event.save(update_fields=["booked_slots"])

            except IntegrityError:
                messages.warning(
                    request,
                    "A ticket has already been booked using this phone number for this event."
                )
                return redirect("events")

            # Email confirmation
            html_content = f"""
                <div>
                    <h2 style='color: #3542D4; text-align: center;'>Eventify</h2>

                    <p>Hi <strong>{ticket.full_name}</strong>,</p>

                    <p>
                        You have successfully booked a ticket.
                        Find your event details below:
                    </p>

                    <h3>Event Details</h3>

                    <ul>
                        <li><strong>Ticket ID:</strong> #{ticket.id}</li>
                        <li><strong>Number of Tickets:</strong> {ticket.tickets}</li>
                        <li><strong>Event:</strong> {event.event_name}</li>
                        <li><strong>Location:</strong> {event.event_location}</li>
                        <li>
                            <strong>Date & Time:</strong>
                            {event.event_date} &middot;
                            {event.start_time.strftime("%I:%M %p")}
                        </li>
                        <li>
                            <strong>Price:</strong>
                            {"Free" if event.is_free else f"Ksh {event.event_price} per ticket"}
                        </li>
                    </ul>

                    <p>
                        Please present this email at the event entrance.
                        If your ticket has a fee, payment shall be done at the entrance.
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

            message = EmailMultiAlternatives(
                subject,
                "",
                from_email,
                to
            )

            message.attach_alternative(html_content, "text/html")
            message.send()

            messages.success(
                request,
                "Ticket booked successfully! A confirmation email has been sent to your email."
            )

            return redirect("events")

    else:
        form = TicketForm()

    return render(request, 'ticket_form.html', {"form": form, "event": event})


def my_tickets(request):
    tickets = []
    searched = False

    if request.method == "POST":
        email = request.POST.get('email', '').strip()

        if not email:
            messages.error(request, "Please enter your booking email address.")
        else:
            searched = True

            # Save the email in the session for ticket detail verification
            request.session['ticket_lookup_email'] = email.lower()

            tickets = Ticket.objects.filter(
                email__iexact=email
            ).select_related('event').order_by('-id')

            if not tickets.exists():
                messages.info(
                    request,
                    "No event bookings were found for this email address. Please check your email and try again."
                )

    return render(request,'my_tickets.html', {'tickets': tickets,'searched': searched})

def ticket_details(request, ticket_id):
    email = request.session.get('ticket_lookup_email')

    if not email:
        return redirect('my_tickets')

    ticket = get_object_or_404(
        Ticket.objects.select_related('event'),
        id=ticket_id,
        email__iexact=email
    )

    event = ticket.event

    # Calculate total booking amount
    if event.is_free:
        total_amount = 0
    else:
        total_amount = event.event_price * ticket.tickets

    return render(request, 'ticket_details.html', {'ticket': ticket,'event': event,'total_amount': total_amount,})

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
                            &copy; {timezone.now().year} Eventify. All rights reserved.
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

def custom_404(request, exception):
    return render(request, '404.html', status=404)

def custom_500(request):
    return render(request, '500.html', status=500)


@login_required
def dashboard(request):
    is_admin = request.user.is_staff or request.user.is_superuser

    if is_admin:
        events_queryset = Event.objects.all()
        dashboard_title = "Platform Admin Dashboard"
    else:
        events_queryset = Event.objects.filter(
            created_by=request.user
        )
        dashboard_title = "Organizer Dashboard"

    events_queryset = events_queryset.order_by("-created_at").prefetch_related(
        "ticket_set"
    )

    event_rows = []

    total_expected_revenue = 0
    total_confirmed_revenue = 0
    total_ticket_bookings = 0
    total_tickets_booked = 0
    total_capacity = 0
    total_remaining_slots = 0

    for event in events_queryset:
        tickets = list(event.ticket_set.all())

        booking_count = len(tickets)
        tickets_booked = sum(ticket.tickets for ticket in tickets)

        remaining_slots = max(
            event.event_slots - tickets_booked, 0
        )

        # Free events have no ticket revenue.
        ticket_price = (
            event.event_price or 0
            if not event.is_free
            else 0
        )

        expected_revenue = ticket_price * event.event_slots
        confirmed_revenue = ticket_price * tickets_booked

        event_rows.append({
            "event": event,
            "booking_count": booking_count,
            "tickets_booked": tickets_booked,
            "remaining_slots": remaining_slots,
            "expected_revenue": expected_revenue,
            "confirmed_revenue": confirmed_revenue,
        })

        total_expected_revenue += expected_revenue
        total_confirmed_revenue += confirmed_revenue
        total_ticket_bookings += booking_count
        total_tickets_booked += tickets_booked
        total_capacity += event.event_slots
        total_remaining_slots += remaining_slots

    # Organizer attendees: only tickets belonging to their own events.
    if not is_admin:
        attendees_queryset = (
            Ticket.objects
            .filter(event__created_by=request.user)
            .select_related("event")
            .order_by("-created_at")
        )

        attendees_paginator = Paginator(attendees_queryset, 10)

        attendees_page = attendees_paginator.get_page(
            request.GET.get("attendees_page")
        )
    else:
        attendees_page = None

    # Use the most recent 10 events for the charts.
    chart_events = event_rows[:10]

    context = {
        "dashboard_title": dashboard_title,
        "is_admin": is_admin,
        "event_rows": event_rows,
        "attendees_page": attendees_page,
        "total_events": len(event_rows),
        "total_ticket_bookings": total_ticket_bookings,
        "total_tickets_booked": total_tickets_booked,
        "total_capacity": total_capacity,
        "total_remaining_slots": total_remaining_slots,
        "total_expected_revenue": total_expected_revenue,
        "total_confirmed_revenue": total_confirmed_revenue,
        "total_users": get_user_model().objects.count() if is_admin else None,

        "chart_labels": [
            row["event"].event_name for row in chart_events
        ],
        "chart_expected": [
            row["expected_revenue"] for row in chart_events
        ],
        "chart_confirmed": [
            row["confirmed_revenue"] for row in chart_events
        ],
        "chart_bookings": [
            row["tickets_booked"] for row in chart_events
        ],
        "chart_remaining": [
            row["remaining_slots"] for row in chart_events
        ],
    }

    return render(request, "dashboard.html", context)


@login_required
def edit_event(request, slug):
    event = get_manageable_event(request, slug)

    if request.method == "POST":
        form = EventForm(
            request.POST,
            request.FILES,
            instance=event
        )

        if form.is_valid():
            updated_event = form.save(commit=False)

            # Preserve the original owner.
            updated_event.created_by = event.created_by
            updated_event.save()

            messages.success(
                request,
                f'"{updated_event.event_name}" was updated successfully.'
            )
            return redirect('dashboard')
    else:
        form = EventForm(instance=event)

    return render(
        request,
        'edit_event.html',
        {
            'form': form,
            'event': event,
        }
    )

def get_manageable_event(request, slug):
    is_admin = request.user.is_staff or request.user.is_superuser

    if is_admin:
        return get_object_or_404(Event, slug=slug)

    return get_object_or_404(
        Event,
        slug=slug,
        created_by=request.user
    )

@login_required
@require_POST
def delete_event(request, slug):
    event = get_manageable_event(request, slug)
    event_name = event.event_name

    event.delete()

    messages.success(
        request,
        f'"{event_name}" was deleted successfully.'
    )
    return redirect('dashboard')


@login_required
def event_attendees(request, slug):
    # Admins can view any event.
    # Organizers can view only their own events.
    event = get_manageable_event(request, slug)

    attendees_queryset = (
        Ticket.objects
        .filter(event=event)
        .order_by("-created_at")
    )

    paginator = Paginator(attendees_queryset, 10)
    attendees_page = paginator.get_page(request.GET.get("page"))

    context = {
        "event": event,
        "attendees_page": attendees_page,
    }

    return render(request, "event_attendees.html", context)
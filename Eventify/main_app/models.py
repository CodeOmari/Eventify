from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

import os
import uuid
from django.conf import settings
from django.utils.text import slugify

# Create your models here.
def generate_unique_name(instance, filename):
    name = uuid.uuid4()
    full_file_name = f'{name}-{filename}'
    return os.path.join("event_images", full_file_name)
class Event(models.Model):
    EVENT_TYPES = [
        ('TECH', 'Tech'),
        ('MUSIC', 'Music'),
        ('ART', 'Art'),
        ('FOOD', 'Food'),
        ('SPORTS', 'Sports'),
        ('BUSINESS', 'Business'),
        ('WORKSHOP', 'Workshop'),
    ]
    organizer = models.CharField(max_length=100)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_events"
    )
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    event_name = models.CharField(max_length=150)
    slug = models.SlugField(unique=True, blank=True, null=True)
    event_date = models.DateField()
    event_description = models.TextField()
    event_location = models.CharField(max_length=100)
    start_time = models.TimeField()
    end_time = models.TimeField()
    event_image = models.ImageField(upload_to=generate_unique_name, null=True)
    event_price = models.PositiveIntegerField(null=True, blank=True)
    is_free = models.BooleanField(default=False)
    event_slots = models.PositiveIntegerField()
    booked_slots = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.event_name
    
    def get_price(self):
        if self.is_free or not self.event_price:
            return "Free"
        return f"Ksh {self.event_price}"
    
    def remaining_slots(self):
        return self.event_slots - self.booked_slots

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.event_name)
            slug = base_slug
            counter = 1

            while Event.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)
    
    class Meta:
        db_table = 'events'


class Ticket(models.Model):
    full_name = models.CharField(max_length=150)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    slug = models.SlugField(unique=True, blank=True, null=True)
    tickets = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1),MaxValueValidator(5)])
    email = models.EmailField()
    phone_number = models.CharField(max_length=10, blank=True, null=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.full_name} - {self.phone_number} - {self.event}'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = f"ticket-{uuid.uuid4().hex[:12]}"

        super().save(*args, **kwargs)
    
    class Meta:
        db_table = 'tickets'
        constraints = [
            # One booking record per email for each event.
            models.UniqueConstraint(
                fields=['event', 'email'],
                name='unique_email_per_event'
            ),

            # One phone number per event.
            models.UniqueConstraint(
                fields=['event', 'phone_number'],
                name='unique_phone_per_event'
            ),
        ]
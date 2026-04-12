from django.db import models

import os
import uuid

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
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    event_name = models.CharField(max_length=150)
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
    
    class Meta:
        db_table = 'events'
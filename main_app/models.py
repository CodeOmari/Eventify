import os
import uuid

from django.db import models

# Create your models here.

def generate_unique_name(instance, filename):
    name = uuid.uuid4() #
    full_file_name = f'{name}-{filename}'
    return os.path.join("event_images", full_file_name)

# Create your models here.
class Events(models.Model):
    organizer = models.CharField(max_length=120)
    event_name = models.CharField(max_length=80)
    event_date = models.DateField()
    event_description = models.TextField()
    event_location = models.CharField(max_length=80)
    event_time = models.CharField(max_length=8)
    event_image = models.ImageField(upload_to=generate_unique_name, null=True)
    event_price = models.CharField(max_length=4)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.event_name

    class Meta:
        db_table = 'events'

class Tickets(models.Model):
    first_name = models.CharField(max_length=80)
    last_name = models.CharField(max_length=80)
    phone_number = models.CharField(max_length=20, unique=True)
    amount = models.IntegerField(default=0)
    event_name = models.ForeignKey(Events, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.event_name} - {self.amount}"

    class Meta:
        db_table = 'tickets'


import os
import uuid

from django.db import models
from django.contrib.auth.models import User

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


class Registration(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=100)
    event_name = models.ForeignKey(Events, on_delete=models.CASCADE)
    amount = models.IntegerField()

    def _str_(self):
        return f'{self.user.username} - {self.phone_number} - {self.event_name}'

    class Meta:
        db_table = 'registration'

class Payments(models.Model):
    registration = models.ForeignKey(Registration, on_delete=models.CASCADE)
    merchant_request_id = models.CharField(max_length=100)
    checkout_request_id = models.CharField(max_length=100)
    code = models.CharField(max_length=30, null=True)
    status = models.CharField(max_length=20, default="PENDING")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def _str_(self):
        return f"{self.registration}-{self.code} - {self.status}"

    class Meta:
        db_table = 'payments'
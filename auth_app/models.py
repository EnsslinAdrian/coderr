from django.db import models
from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField

class Profile(models.Model):
    account_type_choices  = [
        ("customer", "Customer"),
        ("business", "Business"),
    ]

    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    file = models.ImageField(upload_to='profileImages/', blank=True)
    location = models.CharField(max_length=50, blank=True)
    tel = models.CharField(max_length=30, blank=True)
    description = models.TextField(max_length=150, blank=True)
    working_hours = models.CharField(max_length=30, blank=True)
    type = models.CharField(max_length=10, choices=account_type_choices, default='customer', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)



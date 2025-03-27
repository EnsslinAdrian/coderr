from django.db import models
from auth_app.models import Profile
from django.contrib.auth.models import User

class Offer(models.Model):
    title = models.CharField(max_length=50)
    image = models.ImageField(upload_to='offerImages/', blank=True, null=True)
    description = models.TextField(max_length=200)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class OfferOption(models.Model):
    offer_type_choices = [
        ("basic", "Basic"),
        ("standard", "Standard"),
        ("premium", "Premium")
    ]
      
    title = models.CharField(max_length=30)
    revisions = models.IntegerField()
    delivery_time_in_days = models.IntegerField()
    price = models.DecimalField(max_digits=5, decimal_places=2)
    features = models.JSONField()   
    offer_type = models.CharField(max_length=10, choices=offer_type_choices, default='basic')
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE)


class Order(models.Model):
    offer_type_choices = [
        ("basic", "Basic"),
        ("standard", "Standard"),
        ("premium", "Premium")
    ]

    status_choises = [
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ]

    customer_user = models.ForeignKey(User, related_name='customer_orders', on_delete=models.PROTECT)
    business_user = models.ForeignKey(User, related_name='business_orders', on_delete=models.PROTECT)
    title = models.CharField(max_length=30)
    revisions = models.IntegerField()
    delivery_time_in_days = models.IntegerField()
    price = models.DecimalField(max_digits=5, decimal_places=2)
    features = models.JSONField()
    offer_type = models.CharField(max_length=10, choices=offer_type_choices, default='basic')
    status = models.CharField(max_length=12, choices=status_choises, default='in_progress')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Review(models.Model):
    business_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_received')
    reviewer = models.ForeignKey(User, related_name='reviews_given', on_delete=models.PROTECT)
    rating = models.IntegerField()
    description = models.TextField(max_length=150)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class BaseInfo(models.Model):
    review_count = models.IntegerField()
    average_rating = models.DecimalField(max_digits=5, decimal_places=2)
    user_count = models.IntegerField()
    offer_count = models.IntegerField()

    

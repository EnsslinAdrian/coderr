from django.contrib import admin
from .models import Order, Offer, Review, BaseInfo

# Register your models here.

admin.site.register(Order)
admin.site.register(Offer)
admin.site.register(Review)
admin.site.register(BaseInfo)
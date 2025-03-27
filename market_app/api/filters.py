from django_filters import rest_framework as filters
from market_app.models import Offer
from django.db.models import Min

from django_filters import rest_framework as filters

class OfferFilter(filters.FilterSet):
    max_delivery_time = filters.NumberFilter(method='filter_by_delivery_time')

    class Meta:
        model = Offer
        fields = ['created_at']

    def filter_by_delivery_time(self, queryset, name, value):
        return queryset.filter(offeroption__delivery_time_in_days__lte=value).distinct()



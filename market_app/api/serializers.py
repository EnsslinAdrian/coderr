from rest_framework import serializers
from market_app.models import Offer, Order, OfferOption, Review, BaseInfo
from auth_app.models import Profile

class OfferOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfferOption
        exclude = ['offer'] 

class OfferSerializer(serializers.ModelSerializer):
    details = serializers.SerializerMethodField()
    min_price = serializers.SerializerMethodField()
    min_delivery_time = serializers.SerializerMethodField()
    user_details = serializers.SerializerMethodField()

    class Meta:
        model = Offer
        fields = [
            'id', 'title', 'description', 'image', 'user',
            'details', 'min_price', 'min_delivery_time', 'user_details',
            'created_at', 'updated_at'
        ]
        extra_kwargs = {
            'user': {'read_only': True}
        }

    def get_details(self, obj):
        return OfferOptionSerializer(obj.offeroption_set.all(), many=True).data

    def to_internal_value(self, data):
        details_data = data.pop('details', [])
        ret = super().to_internal_value(data)
        ret['details'] = details_data
        return ret

    def create(self, validated_data):
        details_data = validated_data.pop('details', [])
        offer = Offer.objects.create(**validated_data)
        OfferOption.objects.bulk_create([
            OfferOption(offer=offer, **opt) for opt in details_data
        ])
        return offer

    def get_min_price(self, obj):
        prices = obj.offeroption_set.values_list('price', flat=True)
        return float(min(prices)) if prices else None

    def get_min_delivery_time(self, obj):
        times = obj.offeroption_set.values_list('delivery_time_in_days', flat=True)
        return min(times) if times else None

    def get_user_details(self, obj):
        profile = getattr(obj.user, 'profile', None)
        return {
            "first_name": getattr(profile, 'first_name', ''),
            "last_name": getattr(profile, 'last_name', ''),
            "username": obj.user.username
        }


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'
        extra_kwargs = {
            'reviewer': {'read_only': True}
        }


class BaseInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = BaseInfo
        fields = '__all__'
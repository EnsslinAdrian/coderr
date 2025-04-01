from rest_framework import serializers
from market_app.models import Offer, Order, OfferOption, Review, BaseInfo
from auth_app.models import Profile

class OfferOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfferOption
        exclude = ['offer'] 

class OfferOptionUrlSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    class Meta:
        model = OfferOption
        fields = ['id', 'url']

    def get_url(self, obj):
        return f"/offerdetails/{obj.id}/" 
        
class OfferSerializer(serializers.ModelSerializer):
    details = serializers.SerializerMethodField()
    min_price = serializers.SerializerMethodField()
    min_delivery_time = serializers.SerializerMethodField()
    user_details = serializers.SerializerMethodField()

    class Meta:
        model = Offer
        fields = [
            'id', 'user', 'title', 'image', 'description', 'created_at', 'updated_at',
            'details', 'min_price', 'min_delivery_time', 'user_details',
        ]
        extra_kwargs = {
            'user': {'read_only': True}
        }

    def create(self, validated_data):
        details_data = validated_data.pop('details', [])
        offer = Offer.objects.create(**validated_data)
        OfferOption.objects.bulk_create([
            OfferOption(offer=offer, **opt) for opt in details_data
        ])
        return offer

    def get_details(self, obj):
        return OfferOptionUrlSerializer(obj.offeroption_set.all(), many=True).data
    
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
    
    def to_internal_value(self, data):
        details_data = data.pop('details', [])
        ret = super().to_internal_value(data)
        ret['details'] = details_data
        return ret

class OfferDetailSerializer(serializers.ModelSerializer):
    details = OfferOptionSerializer(source='offeroption_set', many=True)
    min_price = serializers.SerializerMethodField()
    min_delivery_time = serializers.SerializerMethodField()

    class Meta:
        model = Offer
        fields = [
            'id', 'user', 'title', 'image', 'description', 'created_at', 'updated_at',
            'details', 'min_price', 'min_delivery_time', 
        ]

    def get_details(self, obj):
        return OfferOptionUrlSerializer(obj.offeroption_set.all(), many=True).data
    
    def update(self, instance, validated_data):
        details_data = validated_data.pop('offeroption_set', [])
        instance = super().update(instance, validated_data)

        for detail_data in details_data:
            offer_type = detail_data.get('offer_type')
            option_instance = instance.offeroption_set.filter(offer_type=offer_type).first()
            if option_instance:
                for attr, value in detail_data.items():
                    setattr(option_instance, attr, value)
                option_instance.save()

        return instance
    
    def get_min_price(self, obj):
        prices = obj.offeroption_set.values_list('price', flat=True)
        return float(min(prices)) if prices else None

    def get_min_delivery_time(self, obj):
        times = obj.offeroption_set.values_list('delivery_time_in_days', flat=True)
        return min(times) if times else None

class OfferCreateResponseSerializer(serializers.ModelSerializer):
    details = OfferOptionSerializer(source='offeroption_set', many=True)

    class Meta:
        model = Offer
        fields = [
            'id', 'title', 'image', 'description', 'details'
        ]


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
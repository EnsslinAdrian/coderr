from rest_framework import generics
from .serializers import OrderSerializer, OfferSerializer, OfferOptionSerializer, ReviewSerializer, BaseInfoSerializer
from market_app.models import Order, Offer, OfferOption, Review, BaseInfo
from auth_app.models import Profile
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.db.models import Avg
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from .filters import OfferFilter
from django.db.models import Min
from django.shortcuts import get_object_or_404

class CustomPagination(PageNumberPagination):
    page_size = 6
    page_size_query_param = 'page_size'
    max_page_size = 6

class OrderView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        profile = Profile.objects.filter(user=user).first()
        if not profile:
            return Order.objects.none()
    
        if profile.type == "business":
            return Order.objects.filter(business_user=user)
        else:
            return Order.objects.filter(customer_user=user)
    
    def create(self, request, *args, **kwargs):
        offer_detail_id = request.data.get('offer_detail_id')
        if not offer_detail_id:
            return Response({"error": "offer_detail_id is required."},status=status.HTTP_400_BAD_REQUEST)

        offer_option = OfferOption.objects.filter(id=offer_detail_id).first()
        if not offer_option:
            return Response({"error": "OfferOption not found."},status=status.HTTP_404_NOT_FOUND)

        offer = offer_option.offer
        order = Order.objects.create(
            customer_user=request.user,
            business_user=offer.user,
            title=offer_option.title,
            revisions=offer_option.revisions,
            delivery_time_in_days=offer_option.delivery_time_in_days,
            price=offer_option.price,
            features=offer_option.features,
            offer_type=offer_option.offer_type
        )

        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class OrderSingleView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]


class OffersFrontendCompatibleView(generics.ListCreateAPIView):
    serializer_class = OfferSerializer
    permission_classes = [AllowAny]
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = OfferFilter
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'updated_at', 'title', 'min_price']

    def get_queryset(self):
        queryset = Offer.objects.annotate(min_price=Min('offeroption__price'))

        creator_id = self.request.query_params.get("creator_id")
        if creator_id:
            return queryset.filter(user__id=creator_id)

        user = self.request.user
        if user.is_authenticated:
            profile = Profile.objects.filter(user=user).first()
            if profile and profile.type == "business":
                return queryset

        return queryset

    def perform_create(self, serializer):
        profile = Profile.objects.filter(user=self.request.user).first()
        if not profile or profile.type != 'business':
            raise PermissionError("Nur Business-Accounts dürfen Angebote erstellen.")
        serializer.save(user=self.request.user)

class OfferSingleView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Offer.objects.all()
    serializer_class = OfferSerializer
    permission_classes = [AllowAny]

class OfferOptionSingleView(generics.RetrieveUpdateDestroyAPIView):
    queryset = OfferOption.objects.all()
    serializer_class = OfferOptionSerializer
    permission_classes = [AllowAny]


class ReviewView(generics.ListCreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at', 'updated_at', 'rating']

    def get_queryset(self):
        user = self.request.user
        profile = Profile.objects.filter(user=user).first()

        business_user_id = self.request.query_params.get("business_user_id")
        if business_user_id:
            return Review.objects.filter(business_user__id=business_user_id)

        reviewer_id = self.request.query_params.get("reviewer_id")
        if reviewer_id:
            return Review.objects.filter(reviewer__id=reviewer_id)

        if profile:
            if profile.type == "business":
                return Review.objects.filter(business_user=user)
            return Review.objects.filter(reviewer=user)

        return Review.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        business_user_id = self.request.data.get("business_user")

        business_user = get_object_or_404(User, id=business_user_id)

        if Review.objects.filter(reviewer=user, business_user=business_user).exists():
            raise ValidationError("Du hast diesen Anbieter bereits bewertet.")

        serializer.save(reviewer=user, business_user=business_user)

class ReviewSingleView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]


class BaseView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        business_user_count = Profile.objects.filter(type='business').count()
        offer_count = Offer.objects.count()
        review_count = Review.objects.count()
        avg_rating = Review.objects.aggregate(avg=Avg('rating'))['avg']

        return Response({
            "business_profile_count": business_user_count,
            "offer_count": offer_count,
            "review_count": review_count,
            "average_rating": round(avg_rating or 0, 2)
        })

class BaseSingleView(generics.RetrieveUpdateDestroyAPIView):
    queryset = BaseInfo.objects.all()
    serializer_class = BaseInfoSerializer
    permission_classes = [AllowAny]

class OrderCountView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk): 
        count = Order.objects.filter(
            business_user__id=pk,
            status='in_progress'
        ).count()

        return Response({"order_count": count})
   
class CompletedOrderCountView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk):
        count = Order.objects.filter(
            business_user__id=pk,
            status='completed'
        ).count()

        return Response({"completed_order_count": count})


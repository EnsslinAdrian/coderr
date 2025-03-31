from rest_framework import generics
from .serializers import OrderSerializer, OfferSerializer, OfferOptionSerializer, ReviewSerializer, BaseInfoSerializer, OfferDetailSerializer, OfferCreateResponseSerializer
from market_app.models import Order, Offer, OfferOption, Review, BaseInfo
from auth_app.models import Profile
from rest_framework.exceptions import ValidationError, PermissionDenied, NotFound, NotAuthenticated
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
from .base import CustomBaseView


class CustomPagination(PageNumberPagination):
    page_size = 6
    page_size_query_param = 'page_size'
    max_page_size = 6

class OrderView(CustomBaseView, generics.ListCreateAPIView):
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
        profile = Profile.objects.filter(user=request.user).first()
        if not profile or profile.type != 'customer':
            raise PermissionDenied("Benutzer hat keine Berechtigung.")

        offer_detail_id = request.data.get('offer_detail_id')
        if not offer_detail_id:
            return Response({"error": "Ungültige Anfragedaten"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            offer_detail_id = int(offer_detail_id)
        except (TypeError, ValueError):
            raise ValidationError({"offer_detail_id": "Ungültige Anfragedaten."})

        offer_option = OfferOption.objects.filter(id=offer_detail_id).first()
        if not offer_option:
            return Response({"error": "Das angegebene Angebotsdetail wurde nicht gefunden."}, status=status.HTTP_404_NOT_FOUND)

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

        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class OrderSingleView(CustomBaseView, generics.RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        try:
            return Order.objects.get(pk=self.kwargs['pk'])
        except Order.DoesNotExist:
            raise NotFound('Die Bestellung mit der angegebenen ID wurde nicht gefunden.')

    def update(self, request, *args, **kwargs):
        order = self.get_object()
        if request.user != order.business_user:
            return Response(
                {"detail": "Benutzer hat keine Berechtigung, diese Bestellung zu aktualisieren."}, status=403
            )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied("Benutzer hat keine Berechtigung, die Bestellung zu löschen.")
        super().destroy(request, *args, **kwargs)
        return Response(
            {"message": "Die Bestellung wurde erfolgreich gelöscht. Keine weiteren Inhalte in der Antwort."}, status=204
        )


class OffersFrontendCompatibleView(CustomBaseView, generics.ListCreateAPIView):
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
            raise PermissionDenied("Authentifizierter Benutzer ist kein 'business' Profil.")
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        details = request.data.get("details")

        if not isinstance(details, list) or len(details) != 3:
            raise ValidationError({
                'details': 'Ungültige Anfragedaten oder unvollständige Details.'
            })

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        offer_instance = serializer.instance

        full_serializer = OfferCreateResponseSerializer(offer_instance, context=self.get_serializer_context())
        return Response(full_serializer.data, status=status.HTTP_201_CREATED)

class OfferSingleView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Offer.objects.all()
    serializer_class = OfferDetailSerializer
    permission_classes = [IsAuthenticated]

    def handle_exception(self, exc):
        if isinstance(exc, NotAuthenticated):
            return Response(
                {"detail": "Benutzer ist nicht authentifiziert."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        return super().handle_exception(exc)

    def get_object(self):
            try:
                offer = Offer.objects.get(pk=self.kwargs["pk"])
            except Offer.DoesNotExist:
                raise NotFound(" Das Angebot mit der angegebenen ID wurde nicht gefunden.")

            if self.request.method in ['PATCH', 'PUT', 'DELETE']:
                if offer.user != self.request.user:
                    raise PermissionDenied("Authentifizierter Benutzer ist nicht der Eigentümer des Angebots.")

            return offer
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        from .serializers import OfferCreateResponseSerializer 
        response_serializer = OfferCreateResponseSerializer(instance, context=self.get_serializer_context())

        return Response(response_serializer.data)

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({"message": "Das Angebot wurde erfolgreich gelöscht."}, status=204)
    
class OfferOptionSingleView(generics.RetrieveAPIView):
    queryset = OfferOption.objects.all()
    serializer_class = OfferOptionSerializer
    permission_classes = [AllowAny]

    def get_object(self):
        try:
            return OfferOption.objects.get(pk=self.kwargs["pk"])
        except OfferOption.DoesNotExist:
            raise NotFound("Das Angebotsdetail mit der angegebenen ID wurde nicht gefunden.")


class ReviewView(CustomBaseView, generics.ListCreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at', 'updated_at', 'rating']

    def get_queryset(self):
        queryset = Review.objects.all()
        business_user_id = self.request.query_params.get("business_user_id")
        reviewer_id = self.request.query_params.get("reviewer_id")

        if business_user_id:
            queryset = queryset.filter(business_user__id=business_user_id)

        if reviewer_id:
            queryset = queryset.filter(reviewer__id=reviewer_id)

        return queryset

    def perform_create(self, serializer):
        user = self.request.user
        business_user_id = self.request.data.get("business_user")
        business_user = get_object_or_404(User, id=business_user_id)

        profile = getattr(user, "profile", None)
        if profile and profile.type == "business":
            raise PermissionDenied("Business-Nutzer dürfen keine Bewertungen abgeben.")

        if Review.objects.filter(reviewer=user, business_user=business_user).exists():
            raise ValidationError("Fehlerhafte Anfrage. Der Benutzer hat möglicherweise bereits eine Bewertung für das gleiche Geschäftsprofil abgegeben.")

        serializer.save(reviewer=user, business_user=business_user)

class ReviewSingleView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        try:
            review = Review.objects.get(pk=self.kwargs['pk'])
        except Review.DoesNotExist:
            raise NotFound("Nicht gefunden. Es wurde keine Bewertung mit der angegebenen ID gefunden.")

        if self.request.method in ['PATCH', 'PUT', 'DELETE']:
            if review.reviewer != self.request.user:
                raise PermissionDenied("Der Benutzer ist nicht berechtigt, diese Bewertung zu bearbeiten")

        return review

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({"message": "Erfolgreich gelöscht. Es wird kein Inhalt zurückgegeben."}, status=204)


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

class OrderCountView(CustomBaseView, APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk): 
        count = Order.objects.filter(
            business_user__id=pk,
            status='in_progress'
        ).count()

        return Response({"order_count": count})
   
class CompletedOrderCountView(CustomBaseView, APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        count = Order.objects.filter(
            business_user__id=pk,
            status='completed'
        ).count()

        return Response({"completed_order_count": count})

